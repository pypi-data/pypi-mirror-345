#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
**Note**
Run this program to make of the entire module, repository, installable.

Created: {CREATION_DATE}
Current Version: 4.3.1
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
PACKAGE_NAME = "climalab"
CREATION_DATE = dt.now().strftime(TIME_FMT_STR)

#--------------------------------#
# Define the metadata dictionary #
#--------------------------------#

metadata_dict = dict(
    name=PACKAGE_NAME,
    version="4.3.1",
    description="A Python toolkit for climate data processing and analysis",
    long_description=open("climalab/README.md").read(),
    long_description_content_type="text/markdown",
    author="Jon Ander Gabantxo",
    author_email="jagabantxo@gmail.com",
    url="https://github.com/EusDancerDev/climalab",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "xarray>=0.20.0",
        "netCDF4>=1.6.0",
        "matplotlib>=3.5.0",
        "cartopy>=0.20.0",
        "filewise>=3.7.0",  # Required for file operations
        "pygenutils>=15.11.0",  # Required for system operations and utilities
        "paramlib>=3.4.0",  # Required for parameter handling
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",  # Changed to reflect system requirements
    ],
    license="MIT",
    keywords="climate, data processing, netCDF, visualization, CDO, NCO",
    project_urls={
        "Bug Reports": "https://github.com/EusDancerDev/climalab/issues",
        "Source": "https://github.com/EusDancerDev/climalab",
        "Documentation": "https://github.com/EusDancerDev/climalab#readme",
    },
    # Add system requirements
    system_requires=[
        "cdo>=2.0.0",  # Climate Data Operators
        "nco>=5.0.0",  # NetCDF Operators
    ],
)

# Pass it to the 'setup' module #
setup(**metadata_dict)
