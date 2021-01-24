#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyLSV2


def test_login(address):
    """test to see if login and safe mode works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.login(login=pyLSV2.LSV2.LOGIN_INSPECT) is True
    assert lsv2.login(login=pyLSV2.LSV2.LOGIN_FILETRANSFER) is True
    assert lsv2.login(login=pyLSV2.LSV2.LOGIN_DNC) is False
    lsv2.disconnect()


def test_read_versions(address):
    """test if login and basic query works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_versions() is not False
    lsv2.disconnect()
