#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for file and directory functions"""

import pyLSV2


def test_read_info(address):
    """test if reading of file information works"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.change_directory(remote_directory='TNC:/nc_prog') is True
    assert lsv2.get_directory_info() is not False
    assert lsv2.get_file_info(remote_file_path='TNC:/nc_prog/$mdi.h') is not False
    assert lsv2.get_directory_content() is not False
    assert lsv2.get_drive_info() is not False
    lsv2.disconnect()


def test_directory_functions(address):
    """test if functions to change, create and delete directorys work"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.change_directory('TNC:/nc_prog') is True
    assert lsv2.make_directory('TNC:/nc_prog/pyLSV2_test/T1/T2/T3') is True
    assert lsv2.delete_empty_directory(
        'TNC:/nc_prog/pyLSV2_test/T1/T2/T3') is True
    assert lsv2.change_directory('TNC:/nc_prog/pyLSV2_test/T1/T2/T3') is False
    assert lsv2.change_directory('TNC:/nc_prog/pyLSV2_test/T1/T2') is True
    assert lsv2.delete_empty_directory(
        'TNC:/nc_prog/pyLSV2_test/T1/T2') is False
    assert lsv2.change_directory('TNC:/nc_prog') is True
    assert lsv2.delete_empty_directory(
        'TNC:/nc_prog/pyLSV2_test/T1/T2') is True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test/T1') is True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test') is True
    lsv2.disconnect()


def test_remote_file_functions(address):
    """test if functions for manipulating the remote file system work"""
    lsv2 = pyLSV2.LSV2(address, port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.make_directory('TNC:/nc_prog/pyLSV2_test') is True
    assert lsv2.change_directory('TNC:/nc_prog/pyLSV2_test') is True

    assert lsv2.copy_local_file(
        source_path='TNC:/nc_prog/$mdi.h', target_path='TNC:/nc_prog/pyLSV2_test/') is True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/$mdi.h') is not False

    assert lsv2.copy_local_file(
        source_path='TNC:/nc_prog/$mdi.h', target_path='TNC:/nc_prog/pyLSV2_test/aa.h') is True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/aa.h') is not False

    assert lsv2.copy_local_file(
        source_path='TNC:/nc_prog/$mdi.h', target_path='mdi.b') is True
    assert lsv2.get_file_info('TNC:/nc_prog/mdi.b') is not False

    assert lsv2.change_directory(remote_directory='TNC:/nc_prog') is True
    assert lsv2.copy_local_file(
        source_path='$mdi.h', target_path='TNC:/nc_prog/pyLSV2_test/bb.h') is True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/bb.h') is not False

    assert lsv2.move_local_file(source_path='TNC:/nc_prog/pyLSV2_test/bb.h',
                                target_path='TNC:/nc_prog/pyLSV2_test/cc.h') is True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/cc.h') is not False

    assert lsv2.delete_file('TNC:/nc_prog/pyLSV2_test/cc.h') is True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/cc.h') is False

    assert lsv2.delete_file('TNC:/nc_prog/pyLSV2_test/aa.h') is True
    assert lsv2.delete_file('TNC:/nc_prog/pyLSV2_test/$mdi.h') is True
    assert lsv2.delete_file('TNC:/nc_prog/mdi.b') is True

    assert lsv2.change_directory('TNC:/nc_prog') is True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test') is True
    lsv2.disconnect()
