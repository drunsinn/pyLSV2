#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for establishing a connection"""

import pyLSV2


def test_login(address, timeout):
    """test to see if login and safe mode works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()
    
    assert lsv2.login(login=pyLSV2.Login.INSPECT) is True

    assert lsv2.login(login=pyLSV2.Login.FILETRANSFER) is True
    assert lsv2.logout(login=pyLSV2.Login.FILETRANSFER) is True

    assert lsv2.login(login=pyLSV2.Login.MONITOR) is True
    
    assert lsv2.login(login=pyLSV2.Login.DNC) is False

    lsv2.disconnect()

def test_read_versions(address, timeout):
    """test if login and basic query works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()
    assert lsv2.get_versions() is not False
    lsv2.disconnect()

def test_unsafe_logins(address, timeout):
    """test to see if login without safe mode works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.login(login=pyLSV2.Login.DNC) is True
    lsv2.disconnect()