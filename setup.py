#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import wpparser

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

packages = [
    "wpparser"
]

with open('README.md') as f:
    readme = f.read()

requires = []

long_description = """
wpparser parses wordpress export files and returns them as well formatted
python dictionaries.

---

%s

""" % readme


setup(
    name="wpparser",
    version=wpparser.__version__,
    description="Parse WordPress export files into dictionaries.",
    long_description=long_description,
    author="Martin Sandström",
    author_email="martin@marteinn.se",
    url="https://github.com/marteinn/wpparser",
    packages=packages,
    package_data={"": ["LICENSE",], "wpparser": ["*.txt"]},
    package_dir={"wpparser": "wpparser"},
    include_package_data=True,
    install_requires=requires,
    license="Apache 2.0",
    zip_safe=False,
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7"
    ),
    extras_require={
    },
)
