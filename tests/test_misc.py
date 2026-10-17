#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import tempfile
from pathlib import Path
import pyLSV2
import pyLSV2.misc
import pytest
from pyLSV2.err import LSV2DataException


def test_grab_screen_dump(address: str, timeout: float, port: int):
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


def test_decode_axis_conf_names_from_tnc640_payload():
    """decode the observed selector 20 payload without guessing field meaning"""
    result = bytearray.fromhex(
        "00 0c "
        "00 00 00 01 00 02 00 03 00 04 00 05 00 06 00 07 00 08 00 09 00 0b 00 0c "
        "00 00 00 00 00 00 00 01 00 03 00 01 00 02 00 02 00 02 00 03 00 04 00 04 "
        "58 31 00 59 31 00 5a 31 00 41 31 00 42 31 00 43 31 00 55 31 00 56 31 00 "
        "57 31 00 43 32 00 53 31 00 53 32 00"
    )

    decoded = pyLSV2.misc.decode_axis_conf_names(result)

    assert len(decoded) == 12
    assert decoded[0] == pyLSV2.AxisConfigurationName(0, 0, "X1")
    assert decoded[3] == pyLSV2.AxisConfigurationName(3, 1, "A1")
    assert decoded[-1] == pyLSV2.AxisConfigurationName(12, 4, "S2")


def test_decode_axis_phy_names_from_tnc640_payload():
    """decode physical axis IDs, text values, and names from selector 21"""
    result = bytearray.fromhex(
        "00 05 00 00 00 01 00 02 00 03 00 05 "
        "30 2e 30 30 30 30 30 30 00 "
        "2d 30 2e 30 30 30 30 30 30 00 "
        "30 2e 30 30 30 30 30 30 00 "
        "2d 30 2e 30 30 30 30 30 30 00 "
        "30 2e 30 30 30 30 30 30 00 "
        "58 31 00 59 31 00 5a 31 00 41 31 00 43 31 00"
    )

    decoded = pyLSV2.misc.decode_axis_phy_names(result)

    assert decoded == [
        pyLSV2.AxisPhysicalName(0, "0.000000", "X1"),
        pyLSV2.AxisPhysicalName(1, "-0.000000", "Y1"),
        pyLSV2.AxisPhysicalName(2, "0.000000", "Z1"),
        pyLSV2.AxisPhysicalName(3, "-0.000000", "A1"),
        pyLSV2.AxisPhysicalName(5, "0.000000", "C1"),
    ]


@pytest.mark.parametrize(
    ("decoder", "payload"),
    [
        (pyLSV2.misc.decode_axis_conf_names, bytearray.fromhex("00 01 00 00 00 00")),
        (pyLSV2.misc.decode_axis_phy_names, bytearray.fromhex("00 01 00 00 00")),
    ],
)
def test_decode_axis_names_rejects_malformed_payload(decoder, payload):
    """malformed arrays and unterminated strings should raise a data error"""
    with pytest.raises(LSV2DataException):
        decoder(payload)
