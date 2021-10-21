#!/usr/bin/env python

import os
import re
import sys
from setuptools import find_packages, setup

import wpparser

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()


test_requirements = [
    "pytest>=3",
]

requires = [
    "phpserialize>=1.3",
]

version = ""
with open("wpparser/__init__.py", "r") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

# Convert markdown to rst
try:
    from pypandoc import convert_file
    long_description = convert_file("README.md", "rst")
except:
    long_description = ""

setup(
    name="wpparser",
    version=version,
    description="Parse wordpress export files into a well formatted python dictionary",  # NOQA
    long_description=long_description,
    author="Martin Sandström",
    author_email="martin@marteinn.se",
    url="https://github.com/marteinn/wpparser",
    packages=find_packages(),
    package_data={"": ["LICENSE", ], "wpparser": ["*.txt"]},
    package_dir={"wpparser": "wpparser"},
    include_package_data=True,
    install_requires=requires,
    tests_require=test_requirements,
    license="MIT",
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
