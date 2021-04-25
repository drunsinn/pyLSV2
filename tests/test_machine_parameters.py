#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test to see if machine parameter functions work"""

import pyLSV2


def test_read_machine_parameter(address, timeout):
    """test to see if reading of machine parameters works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    if lsv2.get_versions()['Control'] in ('TNC640', 'TNC620', 'TNC320', 'TNC128'):
        # new stype
        assert lsv2.get_machine_parameter('CfgDisplayLanguage.ncLanguage') is not False
    else:
        # old style
        assert lsv2.get_machine_parameter('7320.0') is not False

    lsv2.disconnect()

def test_rw_machine_parameter(address, timeout):
    """test to see if reading and writing of machine parameters works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    if lsv2.get_versions()['Control'] in ('TNC640', 'TNC620', 'TNC320', 'TNC128'):
        # new stype
        parameter_name = 'CfgDisplayLanguage.ncLanguage'
    else:
        # old style
        parameter_name = '7320.0'

    lsv2.login(pyLSV2.LOGIN_PLCDEBUG)
    current_value = lsv2.get_machine_parameter(parameter_name)
    assert lsv2.set_machine_parameter(parameter_name, current_value, safe_to_disk=False) is not False
    lsv2.logout(pyLSV2.LOGIN_PLCDEBUG)

    lsv2.disconnect()