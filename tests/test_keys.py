#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test to see if keypress functions work"""

import pyLSV2


def test_read_machine_parameter(address, timeout):
    """test to see if reading of machine parameters works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    lsv2.login(pyLSV2.Login.MONITOR)

    assert lsv2.set_keyboard_access(False) is True

    assert lsv2.send_key_code(pyLSV2.KEY_MODE_MANUAL) is True

    assert lsv2.send_key_code(pyLSV2.KEY_MODE_PGM_EDIT) is True

    assert lsv2.set_keyboard_access(True) is True

    lsv2.logout(pyLSV2.Login.MONITOR)

    lsv2.disconnect()