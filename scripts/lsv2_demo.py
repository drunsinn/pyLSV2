#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import time
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

    con.disconnect()
