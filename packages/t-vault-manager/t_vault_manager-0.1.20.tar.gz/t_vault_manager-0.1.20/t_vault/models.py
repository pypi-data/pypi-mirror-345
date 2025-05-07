import os
import re
from abc import ABC, abstractmethod
from binascii import Error as BadBase32Error

import pyotp
import requests
from requests import ConnectionError, HTTPError
from retry import retry
from t_object import ThoughtfulObject

from t_vault.utils import exceptions
from t_vault.utils.bw_port import BW_PORT
from t_vault.utils.logger import logger


class Attachment(ThoughtfulObject):
    """A class representing an attachment with a name, item ID, and URL."""

    name: str
    item_id: str
    url: str


class VaultItem(ThoughtfulObject, ABC):
    """A class representing a vault item."""

    name: str = ""
    item_id: str = ""
    totp_key: str | None = None
    attachments: list[Attachment] = []
    fields: dict[str, str | None] = {}
    url: str | None = None
    url_list: list[str] = []
    username: str | None = None
    password: str | None = None

    @abstractmethod
    def get_attachment(self, attachment_name: str, file_path: str) -> str:
        """Get an attachment by name.

        Args:
            attachment_name: The name of the attachment to retrieve.
            file_path: The path to save the attachment to.

        Returns:
            str: The path to the downloaded attachment.
        """
        raise NotImplementedError()

    @abstractmethod
    def update_password(self, password: str | None = None) -> str:
        """Update the password of the vault item.

        Args:
            password: The new password. If None, a new password will be generated.

        Returns:
            str: The new password.
        """
        raise NotImplementedError()

    def update_custom_fields(self, fields: dict | None = None) -> dict:
        """Update the custom fields of the vault item.

        Args:
            fields: The new custom fields.

        Returns:
            dict: The new custom fields.

        """
        raise NotImplementedError()

    @property
    def otp_now(self) -> str | None:
        """Returns the current TOTP code generated using the TOTP key associated with the instance.

        Returns:
            str: The current TOTP code, or None if no TOTP key is set.
        """
        try:
            return pyotp.TOTP(self.totp_key.replace(" ", "")).now() if self.totp_key else None
        except BadBase32Error as e:
            if match := re.search(r"secret=([A-Z0-9]+)", self.totp_key):
                return pyotp.TOTP(match[1]).now()
            raise exceptions.InvalidTOTPKeyError("Invalid TOTP key") from e

    def __getitem__(self, key):
        """Get an item by key.

        Args:
            key: The key to retrieve the item.

        Returns:
            The item corresponding to the key, or the username if key is "login".
        """
        if key == "login":
            return self.username
        try:
            return self.fields[key]
        except KeyError:
            return getattr(self, key)


class BitWardenItem(VaultItem):
    """A class representing a Bitwarden vault item."""

    collection_id_list: list[str] = []
    folder_id: str | None = None
    notes: str | None = None

    def get_attachment(self, attachment_name: str, file_path: str | None = None) -> str:
        """Get an attachment by name.

        Args:
            attachment_name: The name of the attachment to retrieve.
            file_path: Path to download the attachment.

        Returns:
            str: The path to the downloaded attachment.
        """
        if file_path is None:
            file_path = os.path.join(os.getcwd(), attachment_name)
        attachment = next((attachment for attachment in self.attachments if attachment.name == attachment_name), None)
        if attachment is None:
            raise exceptions.VaultAttatchmentNotFoundError(f"Attachment '{attachment_name}' not found.")

        self._get_attachment_request(attachment, file_path)
        return file_path

    @retry((ConnectionError, HTTPError), tries=7, delay=1, backoff=1)
    def _get_attachment_request(self, attachment: Attachment, file_path: str):
        with requests.get(
            f"http://localhost:{BW_PORT}/object/attachment/{attachment.item_id}",
            params={"id": attachment.item_id, "itemid": self.item_id},
            stream=True,
        ) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    @retry((ConnectionError, HTTPError), tries=7, delay=1, backoff=1)
    def update_password(self, password: str | None = None) -> str:
        """Update the password of the vault item.

        WARNING!!! Before calling this method make sure the account has edit permission

        Args:
            password: The new password. If None, a new password will be generated.

        Returns:
            str: The new password.
        """
        if password is None:
            password = self._generate_password()
        self.password = password
        with requests.get(f"http://localhost:{BW_PORT}/object/item/{self.item_id}") as r:
            r.raise_for_status()
            info = r.json().get("data")
            info["login"]["password"] = self.password
        payload = {
            "type": info["type"],
            "name": info["name"],
            "login": info["login"],
        }
        with requests.put(
            f"http://localhost:{BW_PORT}/object/item/{self.item_id}",
            json=payload,
        ) as r:
            r.raise_for_status()
            if r.json().get("success"):
                logger.info(f"Password updated for {self.name}")
                return self.password
            else:
                raise exceptions.UpdatePasswordError(f"Failed to update password for {self.name}")

    @retry((ConnectionError, HTTPError), tries=7, delay=1, backoff=1)
    def _generate_password(self) -> str:
        """Generate a new password for the vault item."""
        with requests.get(f"http://localhost:{BW_PORT}/generate") as r:
            r.raise_for_status()
            return r.json().get("data").get("data")

    @retry((ConnectionError, HTTPError), tries=7, delay=1, backoff=1)
    def update_custom_fields(self, fields: dict | None = None) -> dict:
        """Update the custom fields of the vault item.

        WARNING!!! Before calling this method make sure the account has edit permission

        Args:
            fields: The new custom fields.

        Returns:
            dict: The new custom fields.
        """
        if fields is None:
            raise exceptions.UpdateCustomFieldsError("Custom fields not provided.")

        self.fields = fields
        with requests.get(f"http://localhost:{BW_PORT}/object/item/{self.item_id}") as r:
            r.raise_for_status()
            info = r.json().get("data")
            updated_fields: list = []
            for key, value in self.fields.items():
                info_item: dict = [x for x in info["fields"] if x["name"] == key][0]
                info_item["value"] = self.fields[key]
                updated_fields.append(info_item)

        payload = {
            "organizationId": info["organizationId"],
            "collectionIds": info["collectionIds"],
            "folderId": info["folderId"],
            "type": info["type"],
            "name": info["name"],
            "notes": info["notes"],
            "favorite": info["favorite"],
            "fields": updated_fields,
            "login": info["login"],
            "reprompt": info["reprompt"],
        }
        with requests.put(
            f"http://localhost:{BW_PORT}/object/item/{self.item_id}",
            json=payload,
        ) as r:
            r.raise_for_status()
            if r.json().get("success"):
                logger.info(f"Custom fields updated for {self.name}")
                for field in self.fields:
                    logger.info(f"{field}: {self.fields[field]}")
                return self.fields
            else:
                raise exceptions.UpdateCustomFieldsError(f"Failed to update custom fields for {self.name}")
