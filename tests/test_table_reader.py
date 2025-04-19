#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests if table functions work"""

import pyLSV2


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
