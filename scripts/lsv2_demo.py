#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import tempfile
import time
from pathlib import Path

import pyLSV2

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    address = '192.168.56.101'
    if len(sys.argv) > 1:
        address = sys.argv[1]

    print('Connecting to {}'.format(address))

    con = pyLSV2.LSV2(address, port=19000, timeout=5, safe_mode=False)
    con.connect()

    print('Connected to "{Control}" with NC Software "{NC_Version}"'.format(**con.get_versions()))
    print('Running LSV2 Version {LSV2_Version} with Flags {LSV2_Version_Flags}'.format(**con.get_system_parameter()))

    print('Drive Info: {}'.format(con.get_drive_info()))
    print('Current Folder {Path} Free Space: {Free Size} Attrib: {Dir_Attributs}'.format(**con.get_directory_info()))

    print('PLC Marker: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.PLC_MEM_TYPE_MARKER, count=15)))
    print('PLC Word: {}'.format(con.read_plc_memory(address=6, mem_type=pyLSV2.PLC_MEM_TYPE_WORD, count=10)))
    print('PLC Double Word: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.PLC_MEM_TYPE_DWORD, count=10)))
    print('PLC String: {}'.format(con.read_plc_memory(address=2, mem_type=pyLSV2.PLC_MEM_TYPE_STRING, count=2)))
    print('PLC Input: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.PLC_MEM_TYPE_INPUT, count=5)))
    print('PLC Word Output: {}'.format(con.read_plc_memory(address=10, mem_type=pyLSV2.PLC_MEM_TYPE_OUTPUT_WORD, count=5)))

    # reading of machine parameter for old an new style names
    if not con.is_itnc():
        # new stype
        print('Current Language: {}'.format(con.get_machine_parameter('CfgDisplayLanguage.ncLanguage')))
    else:
        # old style
        print('Current Language: {}'.format(con.get_machine_parameter('7230.0')))
    
    # changing the value of a machine parameter
    #con.login(pyLSV2.LOGIN_PLCDEBUG)
    #new style: con.set_machine_parameter('CfgDisplayLanguage.ncLanguage', 'CZECH', safe_to_disk=False)
    #old style: con.set_machine_parameter('7230.0', '2', safe_to_disk=False)
    #con.logout(pyLSV2.LOGIN_PLCDEBUG)

    # read program stack
    print('Current Program Stack: {}'.format(con.get_program_stack()))

    # demo for sending key codes
    con.login(pyLSV2.LOGIN_MONITOR)
    con.set_keyboard_access(False)
    con.send_key_code(pyLSV2.KEY_MODE_MANUAL)
    time.sleep(3)
    con.send_key_code(pyLSV2.KEY_MODE_PGM_EDIT)
    con.set_keyboard_access(True)
    con.logout(pyLSV2.LOGIN_MONITOR)

    # demo for reading the current tool with fallback if it is not supported by control
    t_info = con.get_spindle_tool_status()
    if t_info is not False:
        print('Current tool number {Number}.{Index} with Axis {Axis} Length {Length} Radius {Radius}'.format(**t_info))
    else:
        print('Direct reading to current tool not supported for this control type. using backup strategy')
        if con.is_tnc():
            pocket_table_path = 'TNC:/table/tool_p.tch'
            transfer_binary = True
            spindel_lable = '0.0'
        elif con.is_itnc():
            pocket_table_path = 'TNC:/TOOL_P.TCH'
            transfer_binary = False
            spindel_lable = '0'
        else:
            pocket_table_path = 'TNC:/table/ToolAllo.tch'
            transfer_binary = True
            spindel_lable = '0.0'

        with tempfile.TemporaryDirectory(suffix=None, prefix='pyLSV2_') as tmp_dir_name:
            local_recive_path = Path(tmp_dir_name).joinpath('tool_p.tch')
            con.recive_file(local_path=str(local_recive_path), remote_path=pocket_table_path, binary_mode=transfer_binary)
            tr = pyLSV2.TableReader()
            pockets = tr.parse_table(local_recive_path)
            spindel = list(filter(lambda pocket: pocket['P'] == spindel_lable, pockets))[0]
            print('Current tool number {T} with name {TNAME}'.format(**spindel))

    con.disconnect()
