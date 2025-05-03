#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**
Run this program to make of the entire module, repository, installable.

Created: {creation_date}
Current Version: 3.8.2
"""

#----------------#
# Import modules #
#----------------#

from setuptools import setup, find_packages
from datetime import datetime as dt

#-------------------#
# Define parameters #
#-------------------#

TIME_FMT_STR = "%Y-%m-%d %H:%M:%S"
CREATION_DATE = dt.now().strftime(TIME_FMT_STR)

PACKAGE_NAME = "filewise"

#--------------------------------#
# Define the metadata dictionary #
#--------------------------------#

metadata_dict = dict(
    name=PACKAGE_NAME,
    version="3.8.2",
    description="A Python package for efficient file and directory management, featuring tools for bulk renaming, data handling, and format conversion",
    long_description=open("filewise/README.md").read(),
    long_description_content_type="text/markdown",
    author="Jon Ander Gabantxo",
    author_email="jagabantxo@gmail.com",
    url="https://github.com/EusDancerDev/filewise",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3.0",
        "xarray>=0.20.0",
        "numpy>=1.21.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    license="MIT",
    keywords="file management, utilities, python",
    project_urls={
        "Bug Reports": "https://github.com/EusDancerDev/filewise/issues",
        "Source": "https://github.com/EusDancerDev/filewise",
        "Documentation": "https://github.com/EusDancerDev/filewise#readme",
    },
)

# Pass it to the 'setup' module #
setup(**metadata_dict)
