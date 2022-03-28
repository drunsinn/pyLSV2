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
from pyLSV2.const import MemoryType

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    address = "192.168.56.102"
    if len(sys.argv) > 1:
        address = sys.argv[1]

    print("Connecting to {}".format(address))

    con = pyLSV2.LSV2(address, port=19000, timeout=5, safe_mode=False)
    con.connect()

    print(
        'Connected to "{Control}" with NC Software "{NC_Version}"'.format(
            **con.get_versions()
        )
    )
    print(
        "Running LSV2 Version {LSV2_Version} with Flags {LSV2_Version_Flags}".format(
            **con.get_system_parameter()
        )
    )

    print("Drive Info: {}".format(con.get_drive_info()))
    print(
        "Current Folder {Path} Free Space: {Free Size} Attrib: {Dir_Attributs}".format(
            **con.get_directory_info()
        )
    )

    print("Axes positions: {}".format(con.get_axes_location()))

    print(
        "PLC Marker: {}".format(
            con.read_plc_memory(address=0, mem_type=MemoryType.MARKER, count=15)
        )
    )
    print(
        "PLC Word: {}".format(
            con.read_plc_memory(address=6, mem_type=MemoryType.WORD, count=10)
        )
    )
    print(
        "PLC Double Word: {}".format(
            con.read_plc_memory(address=0, mem_type=MemoryType.DWORD, count=10)
        )
    )
    print(
        "PLC String: {}".format(
            con.read_plc_memory(address=2, mem_type=MemoryType.STRING, count=2)
        )
    )
    print(
        "PLC Input: {}".format(
            con.read_plc_memory(address=0, mem_type=MemoryType.INPUT, count=5)
        )
    )
    print(
        "PLC Word Output: {}".format(
            con.read_plc_memory(address=10, mem_type=MemoryType.OUTPUT_WORD, count=5)
        )
    )

    # read values from PLC and other locations with telegram R_DP. Only works on iTNC
    if con.is_itnc():
        print(
            "PLC Double Word 7928: {}".format(con.read_data_path("/PLC/memory/D/7928"))
        )
        print("PLC Constant 1: {}".format(con.read_data_path("/PLC/memory/K/1")))
        print("PLC Marker 211: {}".format(con.read_data_path("/PLC/memory/M/211")))
        print("PLC Byte 7192: {}".format(con.read_data_path("/PLC/memory/B/7192")))
        print("PLC Word 10908: {}".format(con.read_data_path("/PLC/memory/W/10908")))
        print("PLC Input 11: {}".format(con.read_data_path("/PLC/memory/I/11")))
        print("PLC String 30: {}".format(con.read_data_path("/PLC/memory/S/30")))
        print(
            "DOC column of tool 1: {}".format(con.read_data_path("/TABLE/TOOL/T/1/DOC"))
        )
        print("L column of tool 1: {}".format(con.read_data_path("/TABLE/TOOL/T/1/L")))
        print("R column of tool 1: {}".format(con.read_data_path("/TABLE/TOOL/T/1/R")))
        print(
            "PLC column of tool 1: {}".format(con.read_data_path("/TABLE/TOOL/T/1/PLC"))
        )
        print(
            "TMAT column of tool 1: {}".format(
                con.read_data_path("/TABLE/TOOL/T/1/TMAT")
            )
        )
        print(
            "LAST_USE column of tool 1: {}".format(
                con.read_data_path("/TABLE/TOOL/T/1/LAST_USE")
            )
        )

    # reading of machine parameter for old an new style names
    if not con.is_itnc():
        # new stype
        print(
            "Current Language: {}".format(
                con.get_machine_parameter("CfgDisplayLanguage.ncLanguage")
            )
        )
    else:
        # old style
        print("Current Language: {}".format(con.get_machine_parameter("7230.0")))

    # changing the value of a machine parameter
    # con.login(pyLSV2.Login.PLCDEBUG)
    # new style: con.set_machine_parameter('CfgDisplayLanguage.ncLanguage', 'CZECH', safe_to_disk=False)
    # old style: con.set_machine_parameter('7230.0', '2', safe_to_disk=False)
    # con.logout(pyLSV2.Login.PLCDEBUG)

    # read program stack
    print("Current Program Stack: {}".format(con.get_program_stack()))

    # demo for sending key codes
    con.login(pyLSV2.Login.MONITOR)
    con.set_keyboard_access(False)
    con.send_key_code(pyLSV2.KeyCode.MODE_MANUAL)
    time.sleep(3)
    con.send_key_code(pyLSV2.KeyCode.MODE_PGM_EDIT)
    con.set_keyboard_access(True)
    con.logout(pyLSV2.Login.MONITOR)

    # demo for reading the current tool with fallback if it is not supported by control
    t_info = con.get_spindle_tool_status()
    if t_info is not False:
        print(
            "Current tool number {Number}.{Index} with Axis {Axis} Length {Length} Radius {Radius}".format(
                **t_info
            )
        )
    else:
        print(
            "Direct reading to current tool not supported for this control type. using backup strategy"
        )
        if con.is_tnc():
            pocket_table_path = "TNC:/table/tool_p.tch"
            transfer_binary = True
            spindel_lable = "0.0"
        elif con.is_itnc():
            pocket_table_path = "TNC:/TOOL_P.TCH"
            transfer_binary = False
            spindel_lable = "0"
        else:
            pocket_table_path = "TNC:/table/ToolAllo.tch"
            transfer_binary = True
            spindel_lable = "0.0"

        with tempfile.TemporaryDirectory(suffix=None, prefix="pyLSV2_") as tmp_dir_name:
            local_recive_path = Path(tmp_dir_name).joinpath("tool_p.tch")
            con.recive_file(
                local_path=str(local_recive_path),
                remote_path=pocket_table_path,
                binary_mode=transfer_binary,
            )
            tr = pyLSV2.TableReader()
            pockets = tr.parse_table(local_recive_path)
            spindel = list(
                filter(lambda pocket: pocket["P"] == spindel_lable, pockets)
            )[0]
            print("Current tool number {T} with name {TNAME}".format(**spindel))

    # read error messages via LSV2, works only on iTNC controls
    if con.is_itnc():
        e_m = con.get_error_messages()
        print("Number of currently ative error messages: {:d}".format(len(e_m)))
        for i, msg in enumerate(e_m):
            print("Error {:d} : {:s}".format(i, msg["Text"]))

    # list all NC-Programms in TNC partition
    h_files = con.get_file_list(path="TNC:", pattern=r"[\$A-Za-z0-9_-]*\.[hH]$")
    print("Found {:d} Klartext programs: {:}".format(len(h_files), h_files))
    i_files = con.get_file_list(path="TNC:", pattern=r"[\$A-Za-z0-9_-]*\.[iI]$")
    print("Found {:d} DIN/ISO programs: {:}".format(len(i_files), i_files))

    con.disconnect()
