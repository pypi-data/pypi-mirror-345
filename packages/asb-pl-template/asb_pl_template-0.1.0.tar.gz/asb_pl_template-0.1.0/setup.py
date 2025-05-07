#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
import os

VERSION = (0, 1, 0)
__version__ = ".".join([str(x) for x in VERSION])
__author__ = "hujianli94"
__email__ = "your_email@example.com"
__license__ = "MIT"
__description__ = "A simple project template for Ansible"
__url__ = "https://github.com/hujianli94/asb-pl-template"

README = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(README):
    with open(README, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = ""

setuptools.setup(
    name="asb_pl_template",
    version=__version__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.6',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'asb_pl_template = asb_pl_template.cli:main',
        ],
    },
)
