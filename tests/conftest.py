#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config for pytest"""

import pytest


def pytest_addoption(parser):
    """add commandline options to tests"""
    parser.addoption("--address", action="store", help="address of machine or programming station")
    parser.addoption("--timeout", action="store", help="number of seconds for network timeout")
    parser.addoption("--port", action="store", help="port number for network connection")


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


@pytest.fixture
def port(request):
    """process commandline option 'port'"""
    port = request.config.getoption("--port")
    if port is None:
        port = 19000
    return int(port)
