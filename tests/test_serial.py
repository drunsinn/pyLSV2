#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import os
from pathlib import Path
import tempfile
import pytest
import pyLSV2
from pyLSV2 import misc


def test_serial_bcc():
    """test if the BCC checksum calculation works"""

    # example taken from the docs
    con = pyLSV2.LSV2(hostname="", ser_url="loopback")
    assert isinstance(con._llcom, pyLSV2.LSV2RS232)

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
    payload.extend(misc.ustr_to_ba("A_LGINSPECT"))
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


@pytest.mark.skipif(
    os.environ.get("RUN_SERIAL_TESTS") != "1", reason="Manual serial integration test requiring hardware and user interaction"
)
def test_serial_version_read(address: str, timeout: float, port: int):
    """test if establishing a connection via rs232 works"""
    lsv2 = pyLSV2.LSV2(hostname="", port=port, timeout=0.5, safe_mode=True, ser_url="socket://localhost:8888")
    assert isinstance(lsv2._llcom, pyLSV2.LSV2RS232)

    lsv2.connect()
    assert (len(lsv2.versions.control) > 1) is True

    assert isinstance(lsv2.versions.nc_sw_base, int)
    assert isinstance(lsv2.versions.nc_sw_type, int)
    assert isinstance(lsv2.versions.nc_sw_version, int)
    assert isinstance(lsv2.versions.nc_sw_service_pack, int)

    lsv2.disconnect()


@pytest.mark.skipif(
    os.environ.get("RUN_SERIAL_TESTS") != "1", reason="Manual serial integration test requiring hardware and user interaction"
)
def test_serial_file(address: str, timeout: float, port: int):
    """test if establishing a connection via rs232 works"""
    lsv2 = pyLSV2.LSV2(hostname="", port=port, timeout=0.5, safe_mode=True, ser_url="socket://localhost:8888")
    assert isinstance(lsv2._llcom, pyLSV2.LSV2RS232)

    lsv2.connect()

    if lsv2.versions.is_itnc():
        mdi_path = "TNC:\\$MDI.H"
    else:
        mdi_path = "TNC:\\nc_prog\\$mdi.h"

    assert lsv2.change_directory(remote_directory="TNC:\\nc_prog") is True
    assert lsv2.directory_info() is not False
    assert lsv2.file_info(remote_file_path=mdi_path) is not None
    assert lsv2.directory_content() is not False
    assert lsv2.drive_info() is not False

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_mdi_path = Path(tmp_dir_name).joinpath("mdi.h")
        assert lsv2.recive_file(local_path=str(local_mdi_path), remote_path=mdi_path, binary_mode=False) is True

    lsv2.disconnect()
