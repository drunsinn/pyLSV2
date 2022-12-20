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
    assert (len(lsv2.versions.control_version) > 1) is True
    lsv2.disconnect()


def test_context_manager(address, timeout):
    """test if login and basic query works"""
    with pyLSV2.LSV2(address, port=19000, timeout=timeout) as lsv2:
        assert lsv2.versions.control_type is not pyLSV2.ControlType.UNKNOWN


def test_switching_safe_mode(address, timeout):
    """check if enabeling and diabeling safe mode works"""
    with pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True) as lsv2:
        assert lsv2.login(login=pyLSV2.Login.DNC) is False
        lsv2.switch_safe_mode(enable_safe_mode=False)
        assert lsv2.login(login=pyLSV2.Login.DNC) is True
        lsv2.logout(login=pyLSV2.Login.DNC)
        lsv2.switch_safe_mode(enable_safe_mode=True)
        assert lsv2.login(login=pyLSV2.Login.DNC) is False


def test_login_with_password(address, timeout):
    """check if logging in with a password works"""
    with pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False) as lsv2:
        if not (lsv2.versions.control_version.startswith("iTNC530 Programm") or
                lsv2.versions.control_version.startswith("iTNC530Programm")):
            # logon to plc is not locked?
            lsv2.logout(pyLSV2.Login.FILEPLC)
            assert lsv2.login(login=pyLSV2.Login.FILEPLC) is False
            assert lsv2.login(login=pyLSV2.Login.FILEPLC,
                              password="807667") is True


def test_unsafe_logins(address, timeout):
    """test to see if login without safe mode works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.login(login=pyLSV2.Login.DNC) is True
    lsv2.disconnect()
