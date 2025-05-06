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
PACKAGE_NAME = "LinguaLab"
CREATION_DATE = dt.now().strftime(TIME_FMT_STR)

#--------------------------------#
# Define the metadata dictionary #
#--------------------------------#

METADATA_DICT = dict(
    name=PACKAGE_NAME,
    version="3.4.3",
    description="A multilingual text and voice processing toolkit",
    long_description=open("LinguaLab/README.md").read(),
    long_description_content_type="text/markdown",
    author="Jon Ander Gabantxo",
    author_email="jagabantxo@gmail.com",
    url="https://github.com/EusDancerDev/LinguaLab",
    packages=find_packages(),
    python_requires=">=3.9,<3.12",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "filewise>=3.7.0",
        "pygenutils>=15.11.0",
        "paramlib>=3.4.0",
        "SpeechRecognition>=3.10.0",
        "googletrans>=4.0.0",
        "gTTS>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    keywords="language processing, translation, speech recognition, text processing",
    project_urls={
        "Bug Reports": "https://github.com/EusDancerDev/LinguaLab/issues",
        "Source": "https://github.com/EusDancerDev/LinguaLab",
        "Documentation": "https://github.com/EusDancerDev/LinguaLab#readme",
    },
)

# Pass it to the 'setup' module #
setup(**METADATA_DICT)
