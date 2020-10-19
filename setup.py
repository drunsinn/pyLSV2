#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""package configuration for pyLSV2"""
from setuptools import find_packages, setup
from pyLSV2 import __version__

setup(
    name='pyLSV2',
    packages=find_packages(include=['pyLSV2',], exclude=('tests', 'data')),
    version=__version__,
    description='A pure Python3 implementation of the LSV2 protocol',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='drunsinn',
    author_email='dr.unsinn@googlemail.com',
    url='https://github.com/drunsinn/pyLSV2',
    license='MIT',
    install_requires=[],
    scripts=['scripts/check_for_LSV2_commands.py',],
    zip_safe=True,
    keywords="LSV2 cnc communication transfer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: System :: Archiving"
    ],

)
