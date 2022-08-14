   #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config for pytest"""

import pytest


def pytest_addoption(parser):
    """add commandline options to tests"""
    parser.addoption(
        "--address", action="store", help="address of machine or programming station"
    )
    parser.addoption(
        "--timeout", action="store", help="number of seconds for network timeout"
    )


@pytest.fixture
def address(request):
    """process commandline option 'address'"""
    par = request.config.getoption("--address")
    if par is None:
        par = "192.168.56.101"
    return par


@pytest.fixture
def timeout(request):
    """process commandline option 'timeout'"""
    seconds = request.config.getoption("--timeout")
    if seconds is None:
        seconds = 5.0
    return float(seconds)
