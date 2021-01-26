#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config for pytest"""

import pytest


def pytest_addoption(parser):
    """add commandline options to tests"""
    parser.addoption("--address", action="store",
                     help="address of machine or programing station")


@pytest.fixture
def address(request):
    """process commandline option 'address'"""
    par = request.config.getoption("--address")
    if par is None:
        par = '192.168.56.101'
    return par
