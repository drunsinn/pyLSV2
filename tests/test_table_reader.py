#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests if table functions work"""

import importlib
import json

import pyLSV2
from . import test_files


def test_header_parser():
    """test if parsing the header line works as expected"""
    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN 8150-1-en.tab")
    assert data["name"] == "8150-1-en"
    assert data["suffix"] == "tab"
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == ""

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN CCMT.CUT MM")
    assert data["name"] == "CCMT"
    assert data["suffix"] == "CUT"
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN GENERIC.CUTD MM")
    assert data["name"] == "GENERIC"
    assert data["suffix"] == "CUTD"
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN TOOL.T MM")
    assert data["name"] == "TOOL"
    assert data["suffix"] == "T"
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN TOOL.T INCH")
    assert data["name"] == "TOOL"
    assert data["suffix"] == "T"
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "INCH"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN TOOL.T MM Version: 'Update:120.23'")
    assert data["name"] == "TOOL"
    assert data["suffix"] == "T"
    assert data["version"] == "120.23"
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN TOOL.T MM Version: 'Update:120.17 Date:2004-08-01'")
    assert data["name"] == "TOOL"
    assert data["suffix"] == "T"
    assert data["version"] == "120.17"
    assert data["date"] == "2004-08-01"
    assert data["mark"] is None
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN TOOL.T MM Version: 'Update:120.17 Date:2004-08-01' U")
    assert data["name"] == "TOOL"
    assert data["suffix"] == "T"
    assert data["version"] == "120.17"
    assert data["date"] == "2004-08-01"
    assert data["mark"] == "U"
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN Test.AFC.TAB MM")
    assert data["name"] == "Test"
    assert data["suffix"] == "AFC.TAB"
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "MM"

    data = pyLSV2.table_reader.NCTable.parse_header("BEGIN SIMTOOLT_M MM")
    assert data["name"] == "SIMTOOLT_M"
    assert data["suffix"] is None
    assert data["version"] is None
    assert data["date"] is None
    assert data["mark"] is None
    assert data["unit"] == "MM"

def test_tab_read():
    # Tool table from TNC640 programming station
    files = importlib.resources.files(test_files)
    path = files.joinpath("tool.t")
    nc_table = pyLSV2.table_reader.NCTable.parse_table(path)
    assert nc_table.has_unit is True
    assert nc_table.is_metric is True
    assert nc_table.name == "TOOL"
    assert nc_table.suffix == "t"
    assert nc_table.version == "110.24"
    assert len(nc_table.column_names) == 42
    assert len(nc_table.rows) == 7
    assert nc_table.column_names[0] == "T"
    assert nc_table.column_names[1] == "NAME"
    assert nc_table.column_names[40] == "DR2TABLE"
    assert nc_table.column_names[41] == "OVRTIME"
    row = nc_table.rows[0]
    assert row["T"] == "0"
    assert row["NAME"] == "NULLWERKZEUG"
    assert row["OVRTIME"] == ""
    tformat = json.loads(nc_table.format_to_json())
    assert len(tformat["column_list"]) == 42
    assert tformat["column_config"]["T"]["unit"] is None
    assert tformat["column_config"]["T"]["start"] == 0
    assert tformat["column_config"]["T"]["end"] == 8
    assert tformat["column_config"]["OVRTIME"]["unit"] is None
    assert tformat["column_config"]["OVRTIME"]["start"] == 426
    assert tformat["column_config"]["OVRTIME"]["end"] == -1

    # pallet table from MillPlus programming station
    files = importlib.resources.files(test_files)
    path = files.joinpath("palletmag.tab")
    nc_table = pyLSV2.table_reader.NCTable.parse_table(path)
    assert nc_table.has_unit is True
    assert nc_table.is_metric is True
    assert nc_table.name == "PALLETMAG"
    assert nc_table.suffix == "tab"
    assert nc_table.version is None
    assert len(nc_table.column_names) == 5
    assert len(nc_table.rows) == 7
    assert nc_table.column_names[0] == "KEY"
    assert nc_table.column_names[1] == "NAME"
    row = nc_table.rows[0]
    assert row["KEY"] == "0"
    assert row["NAME"] == "Machine"
    assert row["PROGRAM"] == "v:\\program\\4711.pm"
    tformat = json.loads(nc_table.format_to_json())
    assert len(tformat["column_list"]) == 5
    assert tformat["column_config"]["KEY"]["unit"] == "INT"
    assert tformat["column_config"]["KEY"]["start"] == 0
    assert tformat["column_config"]["KEY"]["end"] == 8
    assert tformat["column_config"]["KEY"]["empty_value"] == 0
    assert tformat["column_config"]["KEY"]["min"] == 0
    assert tformat["column_config"]["KEY"]["max"] == 99999999
    assert tformat["column_config"]["KEY"]["unique"] is True
    assert tformat["column_config"]["KEY"]["read_only"] is True
    assert tformat["column_config"]["KEY"]["is_inch"] is False
    assert tformat["column_config"]["NAME"]["unit"] == "TEXT"
    assert tformat["column_config"]["NAME"]["start"] == 8
    assert tformat["column_config"]["NAME"]["end"] == 23
    assert tformat["column_config"]["NAME"]["unique"] is False
    assert tformat["column_config"]["NAME"]["read_only"] is False
    assert tformat["column_config"]["NAME"]["is_inch"] is False

    # Feed/Speed table from iTNC530 programming station
    files = importlib.resources.files(test_files)
    path = files.joinpath("FRAES_GB.CDT")
    nc_table = pyLSV2.table_reader.NCTable.parse_table(path)
    assert nc_table.has_unit is False
    assert nc_table.is_metric is False
    assert nc_table.name == "FRAES_GB"
    assert nc_table.suffix == "cdt"
    assert nc_table.version is None
    assert len(nc_table.column_names) == 7
    assert len(nc_table.rows) == 117
    assert nc_table.column_names[0] == "NR"
    assert nc_table.column_names[1] == "WMAT"
    row = nc_table.rows[0]
    assert row["NR"] == "0"
    assert row["WMAT"] == "St 33-1"
    assert row["Vc2"] == "55"
    assert row["F1"] == "0,016"
    assert row["F2"] == "0,020"
    tformat = json.loads(nc_table.format_to_json())
    assert len(tformat["column_list"]) == 7
    assert tformat["column_config"]["NR"]["unit"] is None
    assert tformat["column_config"]["NR"]["start"] == 0
    assert tformat["column_config"]["NR"]["end"] == 8
    assert tformat["column_config"]["NR"]["empty_value"] is None
    assert tformat["column_config"]["NR"]["min"] is None
    assert tformat["column_config"]["NR"]["max"] is None
    assert tformat["column_config"]["WMAT"]["unit"] == "INT"
    assert tformat["column_config"]["WMAT"]["start"] == 8
    assert tformat["column_config"]["WMAT"]["end"] == 25
    assert tformat["column_config"]["F2"]["unit"] == "FLOAT"
    assert tformat["column_config"]["F2"]["start"] == 66
    assert tformat["column_config"]["F2"]["end"] == -1

