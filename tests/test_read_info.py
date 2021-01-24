#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import pyLSV2


def test_read_pgm_status(address):
    """test if reading the status of the selected program works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=False)
    lsv2.connect()
    assert lsv2.get_program_status() is not False
    lsv2.disconnect()


def test_read_pgm_stack(address):
    """test if reading the program stack works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_program_stack() is not False
    lsv2.disconnect()


def test_read_execution_state(address):
    """test if reading the executions state works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=False)
    lsv2.connect()
    assert lsv2.get_execution_status() in [0, 1, 2, 3, 4, 5]
    lsv2.disconnect()
