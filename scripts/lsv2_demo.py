#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import pyLSV2

logging.basicConfig(level=logging.WARNING)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        address = '192.168.56.101'

    print('Connecting to {}'.format(address))

    con = pyLSV2.LSV2(address, port=19000, timeout=5, safe_mode=False)
    con.connect()

    print('Connected to "{Control}" with NC Software "{NC_Version}"'.format(**con.get_versions()))
    print('Running LSV2 Version {LSV2_Version} with Flags {LSV2_Version_Flags}'.format(**con.get_system_parameter()))

    print('Drive Info: {}'.format(con.get_drive_info()))
    print('Current Folder {Path} Free Space: {Free Size} Attrib: {Dir_Attributs}'.format(**con.get_directory_info()))

    print('PLC Marker: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_MARKER, count=15)))
    print('PLC Word: {}'.format(con.read_plc_memory(address=6, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_WORD, count=10)))
    print('PLC Double Word: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_DWORD, count=10)))
    print('PLC String: {}'.format(con.read_plc_memory(address=2, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_STRING, count=2)))
    print('PLC Input: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_INPUT, count=5)))
    print('PLC Word Output: {}'.format(con.read_plc_memory(address=10, mem_type=pyLSV2.LSV2.PLC_MEM_TYPE_OUTPUT_WORD, count=5)))

    con.disconnect()
