#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test to see if plc functions work"""

import pyLSV2


def test_plc_read(address, timeout):
    """test to see if reading of plc data works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.MARKER, count=1) is not False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.WORD, count=1) is not False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.DWORD, count=1) is not False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.STRING, count=1) is not False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.INPUT, count=1) is not False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.OUTPUT_WORD, count=1) is not False

    lsv2.disconnect()