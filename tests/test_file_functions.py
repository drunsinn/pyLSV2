#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyLSV2

def test_read_info():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.change_directory(remote_directory='TNC:/nc_prog') == True
    assert lsv2.get_directory_info() != False
    assert lsv2.get_file_info(remote_file_path='TNC:/nc_prog/$mdi.h') != False
    assert lsv2.get_directory_content() != False
    assert lsv2.get_drive_info() != False
    lsv2.disconnect()

def test_folder_functions():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.change_directory('TNC:/nc_prog') == True
    assert lsv2.make_directory('TNC:/nc_prog/pyLSV2_test/T1/T2/T3') == True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test/T1/T2/T3') == True
    assert lsv2.change_directory('TNC:/nc_prog/pyLSV2_test/T1/T2/T3') == False
    assert lsv2.change_directory('TNC:/nc_prog/pyLSV2_test/T1/T2') == True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test/T1/T2') == False
    assert lsv2.change_directory('TNC:/nc_prog') == True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test/T1/T2') == True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test/T1') == True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test') == True
    lsv2.disconnect()

def test_remote_file_functions():
    lsv2 = pyLSV2.LSV2('192.168.56.101', port=19000, safe_mode=True)
    lsv2.connect()
    assert lsv2.make_directory('TNC:/nc_prog/pyLSV2_test') == True
    assert lsv2.change_directory('TNC:/nc_prog/pyLSV2_test') == True

    assert lsv2.copy_local_file(source_path='TNC:/nc_prog/$mdi.h', target_path='TNC:/nc_prog/pyLSV2_test/') == True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/$mdi.h') != False

    assert lsv2.copy_local_file(source_path='TNC:/nc_prog/$mdi.h', target_path='TNC:/nc_prog/pyLSV2_test/aa.h') == True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/aa.h') != False

    assert lsv2.copy_local_file(source_path='TNC:/nc_prog/$mdi.h', target_path='mdi.b') == True
    assert lsv2.get_file_info('TNC:/nc_prog/mdi.b') != False

    assert lsv2.change_directory(remote_directory='TNC:/nc_prog') == True
    assert lsv2.copy_local_file(source_path='$mdi.h', target_path='TNC:/nc_prog/pyLSV2_test/bb.h') == True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/bb.h') != False

    assert lsv2.move_local_file(source_path='TNC:/nc_prog/pyLSV2_test/bb.h', target_path='TNC:/nc_prog/pyLSV2_test/cc.h') == True
    assert lsv2.get_file_info('TNC:/nc_prog/pyLSV2_test/cc.h') != False

    assert lsv2.delete_file('TNC:/nc_prog/pyLSV2_test/cc.h') == True
    assert lsv2.delete_file('TNC:/nc_prog/pyLSV2_test/aa.h') == True
    assert lsv2.delete_file('TNC:/nc_prog/pyLSV2_test/$mdi.h') == True
    assert lsv2.delete_file('TNC:/nc_prog/mdi.b') == True

    assert lsv2.change_directory('TNC:/nc_prog') == True
    assert lsv2.delete_empty_directory('TNC:/nc_prog/pyLSV2_test') == True
    lsv2.disconnect()
