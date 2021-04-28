#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for file and directory functions"""

import pyLSV2


def test_read_info(address, timeout):
    """test if reading of file information works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()

    if lsv2.is_itnc():
        mdi_path = 'TNC:/$MDI.H'
    elif lsv2.is_pilot():
        mdi_path = 'TNC:/nc_prog/ncps/PGM01.nc'
    else:
        mdi_path = 'TNC:/nc_prog/$mdi.h'

    assert lsv2.change_directory(remote_directory='TNC:/nc_prog') is True
    assert lsv2.get_directory_info() is not False
    assert lsv2.get_file_info(remote_file_path=mdi_path) is not False
    assert lsv2.get_directory_content() is not False
    assert lsv2.get_drive_info() is not False
    lsv2.disconnect()


def test_directory_functions(address, timeout):
    """test if functions to change, create and delete directories work"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)

    test_dir = 'TNC:/nc_prog/pyLSV2_test/'
    
    lsv2.connect()
    assert lsv2.change_directory('TNC:/nc_prog') is True
    assert lsv2.make_directory(test_dir + 'T1/T2/T3') is True
    assert lsv2.delete_empty_directory(test_dir + 'T1/T2/T3') is True
    assert lsv2.change_directory(test_dir + 'T1/T2/T3') is False
    assert lsv2.change_directory(test_dir + 'T1/T2') is True

    if lsv2.is_itnc():
        assert lsv2.delete_empty_directory(test_dir + 'T1/T2') is True
        assert lsv2.change_directory('TNC:/nc_prog') is True
    else:
        assert lsv2.delete_empty_directory(test_dir + 'T1/T2') is False
        assert lsv2.change_directory('TNC:/nc_prog') is True
        assert lsv2.delete_empty_directory(test_dir + 'T1/T2') is True

    assert lsv2.delete_empty_directory(test_dir + 'T1') is True
    assert lsv2.delete_empty_directory(test_dir) is True
    lsv2.disconnect()


def test_remote_file_functions(address, timeout):
    """test if functions for manipulating the remote file system work"""
    lsv2 = pyLSV2.LSV2(address, port=19000, timeout=timeout, safe_mode=True)
    lsv2.connect()

    test_dir = 'TNC:/nc_prog/pyLSV2_test/'

    if lsv2.is_itnc():
        mdi_dir = 'TNC:/'
        mdi_name = '$MDI.H'
    elif lsv2.is_pilot():
        mdi_dir = 'TNC:/nc_prog/ncps/'
        mdi_name = 'PGM01.nc'
    else:
        mdi_dir = 'TNC:/nc_prog/'
        mdi_name = '$mdi.h'
    
    test_file_1 = test_dir + 'aa.h'
    test_file_2 = test_dir + 'bb.h'
    test_file_3 = test_dir + 'cc.h'

    assert lsv2.make_directory(test_dir) is True
    assert lsv2.change_directory(test_dir) is True

    if lsv2.is_tnc():
        #only test for tnc controls
        assert lsv2.copy_local_file(
            source_path=mdi_dir + mdi_name, target_path=test_dir) is True
        assert lsv2.get_file_info(test_dir + mdi_name) is not False
        assert lsv2.delete_file(test_dir + mdi_name) is True

    assert lsv2.copy_local_file(
        source_path=mdi_dir + mdi_name, target_path=test_file_1) is True
    assert lsv2.get_file_info(test_file_1) is not False

    assert lsv2.change_directory(remote_directory=mdi_dir) is True
    assert lsv2.copy_local_file(
        source_path=mdi_name, target_path=test_file_2) is True

    assert lsv2.get_file_info(test_file_2) is not False

    assert lsv2.move_local_file(source_path=test_file_2,
                                target_path=test_file_3) is True
    assert lsv2.get_file_info(test_file_3) is not False

    assert lsv2.delete_file(test_file_3) is True
    assert lsv2.get_file_info(test_file_3) is False

    assert lsv2.delete_file(test_file_1) is True

    assert lsv2.change_directory(mdi_dir) is True
    assert lsv2.delete_empty_directory(test_dir) is True
    lsv2.disconnect()
