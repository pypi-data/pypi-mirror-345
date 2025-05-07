#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

install_requirements = open("requirements.txt").readlines()

setup(
    author="Thoughtful",
    author_email="support@thoughtful.ai",
    python_requires=">=3.9",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    description="Package for seamless interaction with the Bitwarden.",
    long_description=readme,
    keywords="t_vault",
    name="t_vault_manager",
    packages=find_packages(include=["t_vault", "t_vault.*"]),
    test_suite="tests",
    url="https://www.thoughtful.ai/",
    version="0.1.20",
    zip_safe=False,
    install_requires=install_requirements,
)
