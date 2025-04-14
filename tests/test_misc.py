#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import tempfile
from pathlib import Path
import pyLSV2
import pyLSV2.misc


def test_grab_screen_dump(address: str, timeout: float, port:int):
    """test if creating a screen dump works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=True)
    lsv2.connect()

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_bmp_path = Path(tmp_dir_name).joinpath("test.bmp")
        assert lsv2.grab_screen_dump(local_bmp_path) is True
        assert local_bmp_path.stat().st_size > 1

    lsv2.disconnect()


def test_plc_address_decode():
    """test the decode function for plc memory addresses"""

    assert pyLSV2.misc.decode_plc_memory_address("M0001") == (pyLSV2.const.MemoryType.MARKER, 1)
    assert pyLSV2.misc.decode_plc_memory_address("M0") == (pyLSV2.const.MemoryType.MARKER, 0)
    assert pyLSV2.misc.decode_plc_memory_address("M1") == (pyLSV2.const.MemoryType.MARKER, 1)
    assert pyLSV2.misc.decode_plc_memory_address("M1234") == (pyLSV2.const.MemoryType.MARKER, 1234)

    assert pyLSV2.misc.decode_plc_memory_address("B0") == (pyLSV2.const.MemoryType.BYTE, 0)
    assert pyLSV2.misc.decode_plc_memory_address("W0") == (pyLSV2.const.MemoryType.WORD, 0)
    assert pyLSV2.misc.decode_plc_memory_address("D0") == (pyLSV2.const.MemoryType.DWORD, 0)

    assert pyLSV2.misc.decode_plc_memory_address("B4") == (pyLSV2.const.MemoryType.BYTE, 4)
    assert pyLSV2.misc.decode_plc_memory_address("W4") == (pyLSV2.const.MemoryType.WORD, 2)
    assert pyLSV2.misc.decode_plc_memory_address("D4") == (pyLSV2.const.MemoryType.DWORD, 1)

    assert pyLSV2.misc.decode_plc_memory_address("B16") == (pyLSV2.const.MemoryType.BYTE, 16)
    assert pyLSV2.misc.decode_plc_memory_address("W16") == (pyLSV2.const.MemoryType.WORD, 8)
    assert pyLSV2.misc.decode_plc_memory_address("D16") == (pyLSV2.const.MemoryType.DWORD, 4)

    assert pyLSV2.misc.decode_plc_memory_address("O8") == (pyLSV2.const.MemoryType.OUTPUT, 8)
    assert pyLSV2.misc.decode_plc_memory_address("OW8") == (pyLSV2.const.MemoryType.OUTPUT_WORD, 4)

    assert pyLSV2.misc.decode_plc_memory_address("I8") == (pyLSV2.const.MemoryType.INPUT, 8)
    assert pyLSV2.misc.decode_plc_memory_address("IW8") == (pyLSV2.const.MemoryType.INPUT_WORD, 4)
