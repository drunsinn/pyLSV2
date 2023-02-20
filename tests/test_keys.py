#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test to see if keypress functions work"""

import time

import pyLSV2


def test_key_press_sim(address: str, timeout: float):
    """test to see if reading of machine parameters works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    lsv2.login(pyLSV2.Login.MONITOR)

    if lsv2.versions.is_tnc7():
        # key access not availible for tnc7?
        pass
    else:
        assert lsv2.set_keyboard_access(False) is True

        assert lsv2.send_key_code(pyLSV2.KeyCode.MODE_MANUAL) is True
        time.sleep(1)
        assert lsv2.execution_state() is pyLSV2.ExecState.MANUAL

        assert lsv2.send_key_code(pyLSV2.KeyCode.MODE_PGM_EDIT) is True
        time.sleep(1)
        assert lsv2.execution_state() is pyLSV2.ExecState.MANUAL

        assert lsv2.send_key_code(pyLSV2.KeyCode.MODE_AUTOMATIC) is True
        time.sleep(1)
        assert lsv2.execution_state() is pyLSV2.ExecState.AUTOMATIC

        assert lsv2.set_keyboard_access(True) is True

        lsv2.logout(pyLSV2.Login.MONITOR)

        lsv2.disconnect()
