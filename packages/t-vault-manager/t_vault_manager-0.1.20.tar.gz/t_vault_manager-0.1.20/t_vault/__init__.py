"""Top-level package for T-Bitwarden."""

__author__ = """Thoughtful"""
__email__ = "support@thoughtful.ai"
__version__ = "__version__ = '0.1.20'"


from .t_vault import (
    bw_login,
    bw_get_item,
    bw_login_from_env,
    bw_get_attachment,
    bw_update_password,
    Bitwarden,
    bw_update_custom_fields,
)
from .models import BitWardenItem, VaultItem, Attachment

__all__ = [
    "bw_login",
    "bw_get_item",
    "bw_login_from_env",
    "bw_get_attachment",
    "bw_update_password",
    "bw_update_custom_fields",
    "Bitwarden",
    "BitWardenItem",
    "VaultItem",
    "Attachment",
]
