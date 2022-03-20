#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""package configuration for pyLSV2"""
from setuptools import find_packages, setup
from pyLSV2 import __version__, __doc__

setup(
    name="pyLSV2",
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
    author="drunsinn",
    author_email="dr.unsinn@googlemail.com",
    url="https://github.com/drunsinn/pyLSV2",
    license="MIT",
    install_requires=[],
    scripts=["scripts/lsv2cmd.py"],
    zip_safe=True,
    keywords="LSV2 cnc communication transfer plc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Archiving",
    ],
)
