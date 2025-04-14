#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import pyLSV2


def test_read_pgm_status(address: str, timeout: float, port:int):
    """test if reading the status of the selected program works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.program_status() in [
        pyLSV2.PgmState.CANCELLED,
        pyLSV2.PgmState.ERROR,
        pyLSV2.PgmState.ERROR_CLEARED,
        pyLSV2.PgmState.FINISHED,
        pyLSV2.PgmState.IDLE,
        pyLSV2.PgmState.INTERRUPTED,
        pyLSV2.PgmState.STARTED,
        pyLSV2.PgmState.STOPPED,
    ]
    lsv2.disconnect()


def test_read_pgm_stack(address: str, timeout: float, port:int):
    """test if reading the program stack works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.program_stack() is not False
    lsv2.disconnect()


def test_read_execution_state(address: str, timeout: float, port:int):
    """test if reading the executions state works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.execution_state() in [
        pyLSV2.ExecState.AUTOMATIC,
        pyLSV2.ExecState.MANUAL,
        pyLSV2.ExecState.MDI,
        pyLSV2.ExecState.PASS_REFERENCES,
        pyLSV2.ExecState.SINGLE_STEP,
    ]
    lsv2.disconnect()


def test_read_tool_information(address: str, timeout: float, port:int):
    """test if reading tool information on iTNC works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    if lsv2.versions.is_itnc():
        assert lsv2.spindle_tool_status() is not False
    lsv2.disconnect()


def test_read_override_information(address: str, timeout: float, port:int):
    """test if reading override values works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.override_state() is not False
    lsv2.disconnect()


def test_read_error_messages(address: str, timeout: float, port:int):
    """test if reading error messages on iTNC works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    if lsv2.versions.is_itnc():
        assert lsv2.get_error_messages() is not False
    lsv2.disconnect()


def test_read_axes_location(address: str, timeout: float, port:int):
    """test if reading axis location works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()
    assert lsv2.axes_location() is not False
    lsv2.disconnect()
