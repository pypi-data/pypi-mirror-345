# coding: utf-8

import os
from setuptools import setup, find_packages  # noqa: H301

with open(
    os.path.join(os.path.dirname(__file__), "requirements.txt"), "r"
) as fh:
    requirements = fh.readlines()
# get version from pyproject.toml
with open("pyproject.toml", "r") as fh:
    for line in fh:
        if line.startswith("version ="):
            VERSION = line.split("=")[1].strip().replace('"', '')
            break

if VERSION is None:
    raise ValueError("Version not found in pyproject.toml")

NAME = "openxapi-binance"
PYTHON_REQUIRES = ">= 3.8"

setup(
    name=NAME,
    version=VERSION,
    description="Python client for Binance API",
    author="OpenXAPI",
    author_email="contact@openxapi.com",
    url="https://github.com/openxapi/binance-py",
    keywords=["OpenXAPI","OpenAPI", "binance", "binance-python"],
    install_requires=[req for req in requirements if req.strip()],
    packages=find_packages(exclude=["*.test"]),
    include_package_data=True,
    license="MIT",
    long_description_content_type='text/markdown',
    long_description="""\
    Python client for Binance API
    """,  # noqa: E501
    package_data={"openxapi-binance": ["py.typed"]},
)
