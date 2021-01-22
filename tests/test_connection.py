#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyLSV2

def test_login(address):
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.login(login=pyLSV2.LSV2.LOGIN_INSPECT) == True
    assert lsv2.login(login=pyLSV2.LSV2.LOGIN_FILETRANSFER) == True
    assert lsv2.login(login=pyLSV2.LSV2.LOGIN_DNC) == False
    lsv2.disconnect()

def test_read_versions(address):
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_versions() != False
    lsv2.disconnect()
