#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test to see if plc functions work"""

import pyLSV2


def test_plc_read(address, timeout):
    """test to see if reading of plc data works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    assert lsv2.login(pyLSV2.Login.PLCDEBUG) is True

    assert (
        lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.MARKER, count=1)
        is not False
    )
    assert (
        lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.WORD, count=1)
        is not False
    )
    assert (
        lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.DWORD, count=1)
        is not False
    )
    assert (
        lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.STRING, count=1)
        is not False
    )
    assert (
        lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.INPUT, count=1)
        is not False
    )
    assert (
        lsv2.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.OUTPUT_WORD, count=1)
        is not False
    )

    lsv2.logout(pyLSV2.Login.PLCDEBUG)

    lsv2.disconnect()


def test_data_path_read(address, timeout):
    """test to see if reading via data path works. run only on iTNC"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=False)
    lsv2.connect()

    if lsv2.is_itnc():
        assert lsv2.read_data_path("/PLC/memory/K/1") is not None
        assert lsv2.read_data_path("/PLC/memory/M/1") is not None
        assert lsv2.read_data_path("/PLC/memory/B/1") is not None
        assert lsv2.read_data_path("/PLC/memory/W/2") is not None
        assert lsv2.read_data_path("/PLC/memory/D/4") is not None
        assert lsv2.read_data_path("/PLC/memory/I/1") is not None
        assert lsv2.read_data_path("/PLC/memory/S/1") is not None
        assert lsv2.read_data_path("/TABLE/TOOL/T/1/L") is not None

        # These probably only work on a programming station
        assert (
            lsv2.read_data_path("/PLC/program/symbol/global/MG_BA_Automatik")
            is not None
        )
        assert (
            lsv2.read_data_path(
                '/PLC/program/symbol/module/"SPINDEL.SRC"/KL_100_PROZENT'
            )
            is not None
        )
        assert (
            lsv2.read_data_path(
                "/PLC/program/symbol/global/STG_WZM[0].WL_WZM_SIMULATION_ZAEHLE"
            )
            is not None
        )
        assert lsv2.read_data_path("/PLC/program/symbol/global/+STG_WZM[1]") is not None

        # check if path is sanitized correctly
        assert lsv2.read_data_path("\\PLC\\memory\\K\\1") is not None

    lsv2.disconnect()
