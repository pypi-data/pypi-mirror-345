#!/usr/bin/env python
"""
Setup script for the WireGuard API client.
"""

from setuptools import find_packages, setup

# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements from requirements.txt
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="wg-api-client",
    version="0.1.8",
    description="WireGuard Configuration API Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="TII UAE",
    author_email="info@tii.ae",
    url="https://github.com/tiiuae/wg-api-client-lib",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "wg-api-client=wg_api_client.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking",
    ],
)
