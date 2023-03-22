#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""package configuration for pyLSV2"""
from setuptools import find_packages, setup
from pyLSV2 import __doc__, __version__, __author__, __license__, __email__

setup(
    name="pyLSV2",
    python_requires=">=3.5",
    packages=find_packages(
        include=[
            "pyLSV2",
        ],
        exclude=["tests", "data"],
    ),
    package_data={"pyLSV2": ["locales/*/LC_MESSAGES/*.mo"]},
    include_package_data=True,
    version=__version__,
    description=__doc__,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__email__,
    url="https://github.com/drunsinn/pyLSV2",
    license=__license__,
    install_requires=[],
    scripts=["scripts/lsv2cmd.py", "scripts/tab2csv.py", "scripts/scope2csv.py"],
    keywords="LSV2 cnc communication transfer plc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Archiving",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Typing :: Typed",
    ],
)
