#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test to see if plc functions work"""

import pytest
import pyLSV2


def test_plc_read(address: str, timeout: float, port:int):
    """test to see if reading of plc data works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    assert lsv2.login(pyLSV2.Login.PLCDEBUG) is True

    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.MARKER, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.WORD, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.DWORD, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.STRING, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.OUTPUT_WORD, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.OUTPUT_DWORD, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.INPUT, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.INPUT_WORD, 1) is not False
    assert lsv2.read_plc_memory(0, pyLSV2.MemoryType.INPUT_DWORD, 1) is not False

    lsv2.logout(pyLSV2.Login.PLCDEBUG)

    lsv2.disconnect()


def test_plc_read_marker(address: str, timeout: float, port:int):
    """test reading of plc markers"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    marker_data_0 = lsv2.read_plc_memory(0, pyLSV2.MemoryType.MARKER, 1)
    assert isinstance(marker_data_0, (list,)) is True
    assert (len(marker_data_0) == 1) is True

    marker_data_1 = lsv2.read_plc_memory(1, pyLSV2.MemoryType.MARKER, 1)
    assert isinstance(marker_data_1, (list,)) is True
    assert (len(marker_data_1) == 1) is True

    marker_data = lsv2.read_plc_memory(0, pyLSV2.MemoryType.MARKER, 2)
    assert (len(marker_data) == 2) is True
    assert (marker_data[0] == marker_data_0[0]) is True
    assert (marker_data[1] == marker_data_1[0]) is True

    lsv2.disconnect()


def test_plc_read_string(address: str, timeout: float, port:int):
    """test reading of plc strings"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    data_0 = lsv2.read_plc_memory(0, pyLSV2.MemoryType.STRING, 1)
    assert isinstance(data_0, (list,)) is True
    assert (len(data_0) == 1) is True

    data_1 = lsv2.read_plc_memory(1, pyLSV2.MemoryType.STRING, 1)
    assert isinstance(data_1, (list,)) is True
    assert (len(data_1) == 1) is True

    data = lsv2.read_plc_memory(0, pyLSV2.MemoryType.STRING, 2)
    assert (len(data) == 2) is True
    assert (data[0] == data_0[0]) is True
    assert (data[1] == data_1[0]) is True

    lsv2.disconnect()


def test_plc_read_errors(address: str, timeout: float, port:int):
    """test error states for reading plc data"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    num_words = lsv2.parameters.number_of_words

    with pytest.raises(pyLSV2.LSV2InputException) as exc_info:
        _ = lsv2.read_plc_memory(0, pyLSV2.MemoryType.WORD, (num_words + 1))

    exception_raised = exc_info.value
    assert isinstance(exception_raised, (pyLSV2.LSV2InputException,)) is True

    lsv2.disconnect()


def test_data_path_read(address: str, timeout: float, port:int):
    """test to see if reading via data path works. run only on iTNC"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        assert lsv2.read_data_path("/PLC/memory/K/1") is not None
        assert lsv2.read_data_path("/PLC/memory/M/1") is not None
        assert lsv2.read_data_path("/PLC/memory/B/1") is not None
        assert lsv2.read_data_path("/PLC/memory/W/2") is not None
        assert lsv2.read_data_path("/PLC/memory/D/4") is not None
        assert lsv2.read_data_path("/PLC/memory/I/1") is not None
        assert lsv2.read_data_path("/PLC/memory/S/1") is not None
        assert lsv2.read_data_path("/TABLE/TOOL/T/1/L") is not None

        # These probably only work on a programming station
        assert lsv2.read_data_path("/PLC/program/symbol/global/MG_BA_Automatik") is not None
        assert lsv2.read_data_path('/PLC/program/symbol/module/"SPINDEL.SRC"/KL_100_PROZENT') is not None
        assert lsv2.read_data_path("/PLC/program/symbol/global/STG_WZM[0].WL_WZM_SIMULATION_ZAEHLE") is not None
        assert lsv2.read_data_path("/PLC/program/symbol/global/+STG_WZM[1]") is not None

        # check if path is sanitized correctly
        assert lsv2.read_data_path("\\PLC\\memory\\K\\1") is not None

    lsv2.disconnect()


def test_comapare_values(address: str, timeout: float, port:int):
    """test to see if reading via data path and plc memory returns the same value. run only on iTNC"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 368]:
            v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.DWORD, 1)[0]
            v2 = lsv2.read_data_path("/PLC/memory/D/%d" % (mem_address * 4))
            assert v1 == v2

        for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 368]:
            v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.WORD, 1)[0]
            v2 = lsv2.read_data_path("/PLC/memory/W/%d" % (mem_address * 2))
            assert v1 == v2

        for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 368]:
            v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.BYTE, 1)[0]
            v2 = lsv2.read_data_path("/PLC/memory/B/%d" % (mem_address * 1))
            assert v1 == v2

    lsv2.disconnect()


def test_plc_mem_access(address: str, timeout: float, port:int):
    """test to see if reading via plc address and plc memory returns the same value"""

    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=False)
    lsv2.connect()

    for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 420]:
        v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.DWORD, 1)[0]
        v2 = lsv2.read_plc_address("D%d" % (mem_address * 4))
        assert v1 == v2

    for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 420]:
        v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.WORD, 1)[0]
        v2 = lsv2.read_plc_address("W%d" % (mem_address * 2))
        assert v1 == v2

    for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 420]:
        v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.BYTE, 1)[0]
        v2 = lsv2.read_plc_address("B%d" % (mem_address * 1))
        assert v1 == v2

    for mem_address in [0, 1, 2, 4, 8, 12, 68, 69, 151, 300, 420]:
        v1 = lsv2.read_plc_memory(mem_address, pyLSV2.MemoryType.MARKER, 1)[0]
        v2 = lsv2.read_plc_address("M%d" % (mem_address * 1))
        assert v1 == v2

    lsv2.disconnect()
