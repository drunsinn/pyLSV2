#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for reading file system information"""

import tempfile
from pathlib import Path
import pyLSV2


def test_grab_screen_dump(address: str, timeout: float):
    """test if creating a screen dump works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()

    with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
        local_bmp_path = Path(tmp_dir_name).joinpath("test.bmp")
        assert lsv2.grab_screen_dump(local_bmp_path) is True
        assert local_bmp_path.stat().st_size > 1

    lsv2.disconnect()
