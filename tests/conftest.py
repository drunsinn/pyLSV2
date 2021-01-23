#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest


def pytest_addoption(parser):
    parser.addoption("--address", action="store",
                     help="address of machine or programing station")


@pytest.fixture
def address(request):
    return request.config.getoption("--address")
