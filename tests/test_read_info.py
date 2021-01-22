#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyLSV2


def test_read_pgm_status(address):
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=False)
    lsv2.connect()
    assert lsv2.get_program_status() != False
    lsv2.disconnect()

def test_read_pgm_stack(address):
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_program_stack() != False
    lsv2.disconnect()

def test_read_execution_state(address):
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=False)
    lsv2.connect()
    assert lsv2.get_execution_status() in [0, 1, 2 ,3, 4, 5]
    lsv2.disconnect()
