#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for file transfer functions"""

from importlib import resources
import tempfile
from pathlib import Path
import hashlib

import pyLSV2
from . import test_files


def test_file_recive(address: str, timeout: float, port: int):
    """test if loading a file from the controls works"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=True)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        mdi_path = "TNC:/$MDI.H"
        tool_t_path = "TNC:/TOOL.T"
    elif lsv2.versions.is_pilot():
        mdi_path = "TNC:/nc_prog/ncps/PGM01.nc"
        tool_t_path = "TNC:/table/toolturn.htt"
    elif lsv2.versions.is_millplus():
        mdi_path = "TNC:/mdi/mdi.pm"
        tool_t_path = "TNC:/table/tool.t"
    else:
        mdi_path = "TNC:/nc_prog/$mdi.h"
        tool_t_path = "TNC:/table/tool.t"

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_mdi_path = Path(tmp_dir_name).joinpath("mdi.h")
        assert lsv2.recive_file(local_path=str(local_mdi_path), remote_path=mdi_path, binary_mode=False) is True

        local_tool_table_path = Path(tmp_dir_name).joinpath("tool.t")
        assert lsv2.recive_file(local_path=str(local_tool_table_path), remote_path=tool_t_path) is True

        lsv2.disconnect()


def test_file_transfer_binary(address: str, timeout: float, port: int):
    """test if transferring a file in binary mode works"""
    files = resources.files(test_files)
    local_send_path = files.joinpath("testdata.bmp")

    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=True)
    lsv2.connect()

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_recive_path = Path(tmp_dir_name).joinpath("test.bmp")
        remote_path = pyLSV2.DriveName.TNC + pyLSV2.PATH_SEP + local_send_path.name

        assert lsv2.file_info(remote_path) is not True  # is False doesn't work...

        assert (
            lsv2.send_file(
                local_path=local_send_path,
                remote_path=remote_path,
                override_file=True,
                binary_mode=True,
            )
            is True
        )

        assert (
            lsv2.recive_file(
                local_path=str(local_recive_path),
                remote_path=remote_path,
                override_file=True,
                binary_mode=True,
            )
            is True
        )

        assert lsv2.delete_file(remote_path) is True

        digests = []
        for filename in [local_send_path, local_recive_path]:
            hasher = hashlib.md5()
            with open(filename, "rb") as f_p:
                buf = f_p.read()
                hasher.update(buf)
                h_d = hasher.hexdigest()
                digests.append(h_d)
        assert (digests[0] == digests[1]) is True

    lsv2.disconnect()


def test_file_transfer_comp_mode(address: str, timeout: float, port: int):
    """test if transferring a file with active compatibility mode works. This is to test if transfer without
    secure file transfer works as expected."""
    files = resources.files(test_files)
    local_send_path = files.joinpath("testdata.bmp")
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=True, compatibility_mode=True)
    lsv2.connect()

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_recive_path = Path(tmp_dir_name).joinpath("test.bmp")
        remote_path = pyLSV2.DriveName.TNC + pyLSV2.PATH_SEP + local_send_path.name

        assert lsv2.file_info(remote_path) is not True

        assert lsv2.send_file(local_path=local_send_path, remote_path=remote_path, override_file=True, binary_mode=True) is True

        assert lsv2.recive_file(local_path=str(local_recive_path), remote_path=remote_path, override_file=True, binary_mode=True) is True

        assert lsv2.delete_file(remote_path) is True

        digests = []
        for filename in [local_send_path, local_recive_path]:
            hasher = hashlib.md5()
            with open(filename, "rb") as f_p:
                buf = f_p.read()
                hasher.update(buf)
                h_d = hasher.hexdigest()
                digests.append(h_d)
        assert (digests[0] == digests[1]) is True

    lsv2.disconnect()


def test_recive_with_path_formating(address: str, timeout: float, port: int):
    """test if reading of file information with / instead of \\ as path separator"""
    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=True)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        mdi_path = "TNC:/$MDI.H"
    elif lsv2.versions.is_pilot():
        mdi_path = "TNC:/nc_prog/ncps/PGM01.nc"
    elif lsv2.versions.is_millplus():
        mdi_path = "TNC:/mdi/mdi.pm"
    else:
        mdi_path = "TNC:/nc_prog/$mdi.h"

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_mdi_path = Path(tmp_dir_name).joinpath("mdi.h")
        assert lsv2.recive_file(local_path=str(local_mdi_path), remote_path=mdi_path, binary_mode=False) is True

    lsv2.disconnect()



def test_table_merge_functions(address: str, timeout: float, port: int):
    """test if functions for manipulating the remote file system work"""
    files = resources.files(test_files)
    mt500 = files.joinpath("mergetool500.t")
    mt500_up = files.joinpath("mergetool500up.t")
    mt501 = files.joinpath("mergetool501.t")

    lsv2 = pyLSV2.LSV2(address, port=port, timeout=timeout, safe_mode=True)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        # this function only works on iTNC530
        with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
            local_recive_path = Path(tmp_dir_name).joinpath("ORGTOOL.T")
            local_table_path = Path(tmp_dir_name).joinpath("TEMP.T")

            lsv2.copy_remote_file(source_path="TNC:/TOOL.T", target_path="TOOL_BAK.T")

            lsv2.recive_file(remote_path="TNC:/TOOL.T", local_path=local_recive_path)
            nc_table = pyLSV2.table_reader.NCTable.parse_table(local_recive_path)
            assert len(nc_table.rows) > 0

            tool500 = next((tool for tool in nc_table.rows if tool.get("T") == "500"), None)
            tool501 = next((tool for tool in nc_table.rows if tool.get("T") == "501"), None)
            assert tool500 is None, "Tool 500 already exists in tool table"
            assert tool501 is None, "Tool 501 already exists in tool table"

            with mt500.open("r") as tab_resource:
                tmp_tab_path = Path(tmp_dir_name).joinpath("TEMPTOOL.T")
                with open(tmp_tab_path, "w") as destination:
                    destination.write(tab_resource.read())
                lsv2.send_file(local_path=tmp_tab_path, remote_path="TNC:/TOOL.T", merge_mode=True)
            lsv2.recive_file(remote_path="TNC:/TOOL.T", local_path=local_table_path, override_file=True)
            nc_table = pyLSV2.table_reader.NCTable.parse_table(local_table_path)
            tool500 = next((tool for tool in nc_table.rows if tool.get("T") == "500"), None)
            assert tool500 is not None, "Tool 500 wasn't added to tool table"

            with mt501.open("r") as tab_resource:
                tmp_tab_path = Path(tmp_dir_name).joinpath("TEMPTOOL.T")
                with open(tmp_tab_path, "w") as destination:
                    destination.write(tab_resource.read())
                lsv2.send_file(local_path=tmp_tab_path, remote_path="TNC:/TOOL.T", merge_mode=True)
            lsv2.recive_file(remote_path="TNC:/TOOL.T", local_path=local_table_path, override_file=True)
            nc_table = pyLSV2.table_reader.NCTable.parse_table(local_table_path)
            tool500 = next((tool for tool in nc_table.rows if tool.get("T") == "500"), None)
            tool501 = next((tool for tool in nc_table.rows if tool.get("T") == "501"), None)
            assert tool500 is not None, "Tool 500 was removed from table"
            assert tool500["NAME"] == "TESTTOOL500"
            assert tool501 is not None, "Tool 501 wasn't added to tool table"

            with mt500_up.open("r") as tab_resource:
                tmp_tab_path = Path(tmp_dir_name).joinpath("TEMPTOOL.T")
                with open(tmp_tab_path, "w") as destination:
                    destination.write(tab_resource.read())
                lsv2.send_file(local_path=tmp_tab_path, remote_path="TNC:/TOOL.T", merge_mode=True)
            lsv2.recive_file(remote_path="TNC:/TOOL.T", local_path=local_table_path, override_file=True)
            nc_table = pyLSV2.table_reader.NCTable.parse_table(local_table_path)
            tool500 = next((tool for tool in nc_table.rows if tool.get("T") == "500"), None)
            assert tool500 is not None, "Tool 500 was removed from table"
            assert tool500["NAME"] == "TESTTOOL500_2", "Name of tool 500 was not updated"

            #lsv2.copy_remote_file(source_path="TNC:/TOOL_BAK.T", target_path="TOOL.T")
            #lsv2.delete_file("TNC:/TOOL_BAK.T")

    lsv2.disconnect()
