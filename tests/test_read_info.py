#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyLSV2


def test_read_pgm_status():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_program_status() != False
    lsv2.disconnect()

def test_read_pgm_stack():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_program_stack() != False
    lsv2.disconnect()

def test_read_execution_state():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_execution_status() != False
    lsv2.disconnect()
