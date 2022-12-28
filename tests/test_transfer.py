#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for file transfer functions"""

import tempfile
from pathlib import Path
import hashlib
import pyLSV2


def test_file_recive(address, timeout):
    """test if loading a file from the controls works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        mdi_path = "TNC:/$MDI.H"
        tool_t_path = "TNC:/TOOL.T"
    elif lsv2.versions.is_pilot():
        mdi_path = "TNC:/nc_prog/ncps/PGM01.nc"
        tool_t_path = "TNC:/table/toolturn.htt"
    else:
        mdi_path = "TNC:/nc_prog/$mdi.h"
        tool_t_path = "TNC:/table/tool.t"

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_mdi_path = Path(tmp_dir_name).joinpath("mdi.h")
        assert (
            lsv2.recive_file(
                local_path=str(local_mdi_path), remote_path=mdi_path, binary_mode=False
            )
            is True
        )

        local_tool_table_path = Path(tmp_dir_name).joinpath("tool.t")
        assert (
            lsv2.recive_file(
                local_path=str(local_tool_table_path), remote_path=tool_t_path
            )
            is True
        )

        lsv2.disconnect()


def test_file_transfer_binary(address, timeout):
    """test if transferring a file in binary mode works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_send_path = Path("./data/testdata.bmp")
        local_recive_path = Path(tmp_dir_name).joinpath("test.bmp")
        remote_path = pyLSV2.DriveName.TNC + pyLSV2.PATH_SEP + local_send_path.name

        assert lsv2.get_file_info(remote_path) is not True  # is False doesn't work...

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


def test_recive_with_path_formating(address, timeout):
    """test if reading of file information with / instead of \\ as path separator"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()

    if lsv2.versions.is_itnc():
        mdi_path = "TNC:/$MDI.H"
    elif lsv2.versions.is_pilot():
        mdi_path = "TNC:/nc_prog/ncps/PGM01.nc"
    else:
        mdi_path = "TNC:/nc_prog/$mdi.h"

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_mdi_path = Path(tmp_dir_name).joinpath("mdi.h")
        assert (
            lsv2.recive_file(
                local_path=str(local_mdi_path), remote_path=mdi_path, binary_mode=False
            )
            is True
        )

    lsv2.disconnect()
