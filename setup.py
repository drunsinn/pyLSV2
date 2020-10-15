#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""package configuration for pyLSV2"""
from setuptools import find_packages, setup
from pyLSV2 import __version__

setup(
    name='pyLSV2',
    packages=find_packages(include=['pyLSV2']),
    version=__version__,
    description='A pure Python3 implementation of the LSV2 protocol',
    long_description=open('README.md').read(),
    author='drunsinn',
    author_email='dr.unsinn@googlemail.com',
    license='MIT',
    install_requires=[]
)
