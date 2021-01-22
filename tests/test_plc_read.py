#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyLSV2

def test_login():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=False)
    lsv2.connect()

    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_MARKER, count=1) != False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_WORD, count=1) != False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_DWORD, count=1) != False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_STRING, count=1) != False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_INPUT, count=1) != False
    assert lsv2.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_OUTPUT_WORD, count=1) != False

    lsv2.disconnect()