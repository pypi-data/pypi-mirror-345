#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**
Run this program to make of the entire module, repository, installable.

Created: {CREATION_DATE}
Current Version: 3.4.3
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

PACKAGE_NAME = "statflow"

#--------------------------------#
# Define the metadata dictionary #
#--------------------------------#

METADATA_DICT = dict(
    name=PACKAGE_NAME,
    version="3.4.3",
    description="A versatile statistical toolkit for Python, featuring core statistical methods, time series analysis, signal processing, and climatology tools",
    long_description=open("statflow/README.md").read(),
    long_description_content_type="text/markdown",
    author="Jon Ander Gabantxo",
    author_email="jagabantxo@gmail.com",
    url="https://github.com/EusDancerDev/statflow",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "xarray>=0.20.0",
        "filewise>=3.7.0",
        "pygenutils>=15.11.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    license="MIT",
    keywords="statistics, time series, signal processing, climatology, python",
    project_urls={
        "Bug Reports": "https://github.com/EusDancerDev/statflow/issues",
        "Source": "https://github.com/EusDancerDev/statflow",
        "Documentation": "https://github.com/EusDancerDev/statflow#readme",
    },
)

# Pass it to the 'setup' module #
setup(**METADATA_DICT)
