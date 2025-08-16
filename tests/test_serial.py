#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import pyLSV2


def test_serial_bcc():
    """test if the BCC checksum calculation works"""

    # example taken from the docs
    payload = bytearray()
    payload.extend(pyLSV2.const.BYTE_DLE)
    payload.extend(pyLSV2.const.BYTE_STX)
    payload.extend("TNC 425".encode("utf-8"))
    payload.extend(pyLSV2.const.BYTE_DLE)
    payload.extend(pyLSV2.const.BYTE_ETX)
    assert payload == bytearray([0x10, 0x02, 0x54, 0x4E, 0x43, 0x20, 0x34, 0x32, 0x35, 0x10, 0x03])
    bcc = pyLSV2.low_level_com.LSV2RS232.calculate_bcc(payload)
    assert bcc == 73

    # example taken captured serial communication
    payload = bytearray()
    payload.extend(pyLSV2.const.BYTE_DLE)
    payload.extend(pyLSV2.const.BYTE_STX)
    payload.extend(pyLSV2.misc.ustr_to_ba("A_LGINSPECT"))
    payload.extend(pyLSV2.const.BYTE_DLE)
    payload.extend(pyLSV2.const.BYTE_ETX)
    assert payload == bytearray([0x10, 0x02, 0x41, 0x5F, 0x4C, 0x47, 0x49, 0x4E, 0x53, 0x50, 0x45, 0x43, 0x54, 0x00, 0x10, 0x03])
    bcc = pyLSV2.low_level_com.LSV2RS232.calculate_bcc(payload)
    assert bcc == ord("@")  # Expected BCC value for the given payload
