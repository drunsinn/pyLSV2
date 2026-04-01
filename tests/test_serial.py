#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import pytest
import importlib

import pyLSV2


def test_serial_bcc():
    """test if the BCC checksum calculation works"""

    # example taken from the docs
    con = pyLSV2.LSV2(hostname="", ser_url="loopback")
    payload = bytearray()
    payload.extend((pyLSV2.const.BYTE_DLE, pyLSV2.const.BYTE_STX))
    payload.extend("TNC 425".encode("ascii"))
    payload.extend((pyLSV2.const.BYTE_DLE, pyLSV2.const.BYTE_ETX))
    assert payload == bytearray([0x10, 0x02, 0x54, 0x4E, 0x43, 0x20, 0x34, 0x32, 0x35, 0x10, 0x03])
    bcc = con._llcom.calculate_bcc(payload)
    assert bcc == 73

    # example taken captured serial communication
    payload = bytearray()
    payload.extend((pyLSV2.const.BYTE_DLE, pyLSV2.const.BYTE_STX))
    payload.extend(pyLSV2.misc.ustr_to_ba("A_LGINSPECT"))
    payload.extend((pyLSV2.const.BYTE_DLE, pyLSV2.const.BYTE_ETX))
    assert payload == bytearray([0x10, 0x02, 0x41, 0x5F, 0x4C, 0x47, 0x49, 0x4E, 0x53, 0x50, 0x45, 0x43, 0x54, 0x00, 0x10, 0x03])
    bcc = con._llcom.calculate_bcc(payload)
    assert bcc == ord("@")

    payload = bytearray(
        b"\x10\x02S_PR\x00\x01\xdc\xd0\x00\x00\x9c@\x00\x02y\x10\x00\x00\x03\xe8\x00\x02|\xf8\x00\x00\x03\xe8\x00\x02\x80\xe0\x00\x00\x00\x90\x00\x02\x81p\x00\x00\x03\xe8\x00\x00\x00@\x00\x01\xd4\xc0\x00\x02\x85X\x00\x00\x01\x90\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x01\xd5\x00\x00\x00\x03\xe8\x00\x01\xd8\xe8\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x9f\x0f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x16\xfd\x00\x80\x00 `8\x9an\x10\x03"
    )
    bcc = con._llcom.calculate_bcc(payload)
    assert bcc == 68

    payload = bytearray(
        b"\x10\x02S_PR\x00\x01\xdc\xd0\x00\x00\x9c@\x00\x02y\x10\x10\x00\x00\x03\xe8\x00\x02|\xf8\x00\x00\x03\xe8\x00\x02\x80\xe0\x00\x00\x00\x90\x00\x02\x81p\x00\x00\x03\xe8\x00\x00\x00@\x00\x01\xd4\xc0\x00\x02\x85X\x00\x00\x01\x90\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x01\xd5\x00\x00\x00\x03\xe8\x00\x01\xd8\xe8\x00\x00\x03\xe8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x9f\x0f\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x16\xfd\x00\x80\x00 `8\x9an\x10\x03"
    )
    bcc = con._llcom.calculate_bcc(con._llcom._strip_escaped_bytes(payload))
    assert bcc == 68


@pytest.mark.skipif(not importlib.util.find_spec("serial"), reason="requires the pyserial library")
def test_serial_version_read(address: str, timeout: float, port: int):
    """test if establishing a connection via rs232 works"""
    lsv2 = pyLSV2.LSV2(hostname="", port=port, timeout=timeout, safe_mode=True, ser_url="socket://localhost:8888")
    lsv2.connect()
    assert (len(lsv2.versions.control) > 1) is True

    assert isinstance(lsv2.versions.nc_sw_base, int)
    assert isinstance(lsv2.versions.nc_sw_type, int)
    assert isinstance(lsv2.versions.nc_sw_version, int)
    assert isinstance(lsv2.versions.nc_sw_service_pack, int)

    lsv2.disconnect()

