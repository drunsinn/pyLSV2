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
    return request.config.getoption("--address")
