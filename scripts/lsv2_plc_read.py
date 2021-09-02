#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script contains examples on how to use different functions of pyLSV2
   Not all functions are shown here, especially the file functions aren't shown here
"""
import logging
import sys
import tempfile
import time
from pathlib import Path

import pyLSV2

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    address = '192.168.56.102'
    if len(sys.argv) > 1:
        address = sys.argv[1]

    print('Connecting to {}'.format(address))

    con = pyLSV2.LSV2(address, port=19000, timeout=5, safe_mode=False)
    con.connect()

    print('Connected to "{Control}" with NC Software "{NC_Version}"'.format(**con.get_versions()))
    print('Running LSV2 Version {LSV2_Version} with Flags {LSV2_Version_Flags}'.format(**con.get_system_parameter()))

    #print('PLC Marker: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.MARKER, count=15)))
    #print('PLC Word: {}'.format(con.read_plc_memory(address=6, mem_type=pyLSV2.MemoryType.WORD, count=10)))
    #print('PLC Double Word: {}'.format(con.read_plc_memory(address=7928, mem_type=pyLSV2.MemoryType.DWORD, count=10)))
    #print('PLC String: {}'.format(con.read_plc_memory(address=2, mem_type=pyLSV2.MemoryType.STRING, count=2)))
    #print('PLC Input: {}'.format(con.read_plc_memory(address=0, mem_type=pyLSV2.MemoryType.INPUT, count=5)))
    #print('PLC Word Output: {}'.format(con.read_plc_memory(address=10, mem_type=pyLSV2.MemoryType.OUTPUT_WORD, count=5)))

    print(con.read_data_path('/PLC/memory/D/7928'))

    con.disconnect()
