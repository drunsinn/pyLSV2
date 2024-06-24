#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script contains examples on how to use different functions of pyLSV2
   Not all functions are shown here
"""
import sys
import argparse
import logging
import time
import pyLSV2
from pyLSV2.const import MemoryType


def comprehensive_demo():
    """Basic demo for pyLSV2"""
    parser = argparse.ArgumentParser()

    # parser.add_argument("address", nargs="?", default="192.168.56.101", type=str)

    parser.add_argument("address", help="ip or hostname of control", type=str)

    parser.add_argument(
        "-d",
        "--debug",
        help="Print lots of debugging statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Be verbose",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    print("Connecting to {}".format(args.address))

    with pyLSV2.LSV2(args.address, port=19000, timeout=5) as con:
        con = pyLSV2.LSV2(args.address, port=19000, timeout=5, safe_mode=False)
        con.connect()

        print("Basics:")
        print("# Connected to a '{:s}' running software version '{:s}'".format(con.versions.control, con.versions.nc_sw))
        print(
            "# Version as numeric values base:{:d} type:{:d} version:{:d} service pack:{:d}".format(
                con.versions.nc_sw_base, con.versions.nc_sw_type, con.versions.nc_sw_version, con.versions.nc_sw_service_pack
            )
        )
        print(
            "# Using LSV2 version '{:d}' with version flags '0x{:02x}' and '0x{:02x}'".format(
                con.parameters.lsv2_version,
                con.parameters.lsv2_version_flags,
                con.parameters.lsv2_version_flags_ex,
            )
        )

        if con.versions.nc_sw_type == 4:
            print("# Reading time and date on a windows programming station is not supported")
        elif con.versions.nc_sw_base == 538950:
            print("# Reading time and date on a windows MILLplusIT programming station is not supported")
        else:
            print("# Time and date: {:}".format(con.get_remote_datetime()))

        # read error messages via LSV2, works only on iTNC controls
        print("# read error messages, only available on some iTNC530 versions")
        if con.versions.is_itnc():
            if con.versions.nc_sw_base == 340490 and con.versions.nc_sw_version <= 2:
                print("### control is iTNC but does not support this function")
            else:
                e_m = con.get_error_messages()
                print("## Number of currently active error messages: {:d}".format(len(e_m)))
                for i, msg in enumerate(e_m):
                    print("### Error {:d} : {:s}".format(i, str(msg)))
        else:
            print("## function 'get_error_messages()' not suportet for this control")

        print("Machine:")
        print("# axes positions: {}".format(con.axes_location()))
        exec_stat = con.execution_state()
        exec_stat_text = pyLSV2.get_execution_status_text(exec_stat)
        print("# execution: {:d} - '{:s}'".format(exec_stat, exec_stat_text))
        pgm_stat = con.program_status()
        pgm_stat_text = pyLSV2.get_program_status_text(pgm_stat)
        print("# program: {:d} - '{:s}'".format(pgm_stat, pgm_stat_text))

        pgm_stack = con.program_stack()
        if pgm_stack is not None:
            print("# selected program: '{:s}'".format(pgm_stack.main))
            print("## currently execution '{:s}' on line {:d}".format(pgm_stack.current, pgm_stack.line_no))

        ovr_stat = con.override_state()
        if ovr_stat is not None:
            print("# override states: feed {:f}%, rapid {:f}%, spindle {:f}%".format(ovr_stat.feed, ovr_stat.rapid, ovr_stat.spindle))

        print("PLC memory:")
        print("# the first 5 entries for some memory types:")
        print("## marker: {}".format(con.read_plc_memory(0, MemoryType.MARKER, 5)))
        print("## word: {}".format(con.read_plc_memory(0, MemoryType.WORD, 5)))
        print("## double word: {}".format(con.read_plc_memory(0, MemoryType.DWORD, 5)))
        print("## string: {}".format(con.read_plc_memory(0, MemoryType.STRING, 5)))
        print("## input: {}".format(con.read_plc_memory(0, MemoryType.INPUT, 5)))
        print("## output: {}".format(con.read_plc_memory(0, MemoryType.OUTPUT, 5)))
        print("## input word: {}".format(con.read_plc_memory(0, MemoryType.INPUT_WORD, 5)))
        print("## output word: {}".format(con.read_plc_memory(0, MemoryType.OUTPUT_WORD, 5)))
        print("## input dword: {}".format(con.read_plc_memory(0, MemoryType.INPUT_DWORD, 5)))
        print("## output dword: {}".format(con.read_plc_memory(0, MemoryType.OUTPUT_DWORD, 5)))

        print("# data values via data path, only available on some iTNC530")
        if con.versions.is_itnc():
            if con.versions.nc_sw_base == 340490 and con.versions.nc_sw_version <= 2:
                print("### control is iTNC but does not support this function")
            else:
                print("## marker 0: {}".format(con.read_data_path("/PLC/memory/M/0")))
                print("## marker 1: {}".format(con.read_data_path("/PLC/memory/M/1")))
                print("## string 0: {}".format(con.read_data_path("/PLC/memory/S/0")))
                print("## word 10908: {}".format(con.read_data_path("/PLC/memory/W/10908")))
        else:
            print("## function 'read_data_path()' not suportet for this control")
        print("# table values via data path, only available on some iTNC530")
        if con.versions.is_itnc():
            if con.versions.nc_sw_base == 340490 and con.versions.nc_sw_version <= 2:
                print("### control is iTNC but does not support this function")
            else:
                print("## values from tool table for tool T1:")
                print("## DOC column: {}".format(con.read_data_path("/TABLE/TOOL/T/1/DOC")))
                print("## L column: {}".format(con.read_data_path("/TABLE/TOOL/T/1/L")))
                print("## R column: {}".format(con.read_data_path("/TABLE/TOOL/T/1/R")))
        else:
            print("## function 'read_data_path()' not suportet for this control")

        print("Configuration:")
        if con.versions.is_itnc():
            # old style
            lang = con.get_machine_parameter("7230.0")
        else:
            # new style
            lang = con.get_machine_parameter("CfgDisplayLanguage.ncLanguage")
        print("# Value of machine parameter for NC language: {:s}".format(lang))

        if con.versions.is_tnc7():
            print("UI Interface test not available on TNC7?")
        else:
            print("UI Interface:")
            print("# switch to mode manual")
            con.set_keyboard_access(False)
            con.send_key_code(pyLSV2.KeyCode.MODE_MANUAL)
            con.set_keyboard_access(True)
            print("# wait 5 seconds")
            time.sleep(5)
            print("# switch to mode edit")
            con.set_keyboard_access(False)
            con.send_key_code(pyLSV2.KeyCode.MODE_PGM_EDIT)
            con.set_keyboard_access(True)

        print("File access:")
        drv_info = con.drive_info()
        print("# names of disk drives: {:s}".format(", ".join([drv.name for drv in drv_info])))
        dir_info = con.directory_info()
        print("# current directory is '{:s}' with {:d} bytes of free drive space".format(dir_info.path, dir_info.free_size))

        dir_content = con.directory_content()
        only_files = filter(
            lambda f_e: f_e.is_directory is False and f_e.is_drive is False,
            dir_content,
        )

        for file_entry in only_files:
            print("## file name: {:s}, date {:}, size {:d} bytes".format(file_entry.name, file_entry.timestamp, file_entry.size))
        only_dir = filter(lambda f_e: f_e.is_directory is True and f_e.is_drive is False, dir_content)
        for file_entry in only_dir:
            print("## directory name: {:s}, date {:}".format(file_entry.name, file_entry.timestamp))

        # con.change_directory("TNC:/smartNC")
        # print([c.name for c in con.directory_content()])

        print("# file search")
        h_files = con.get_file_list(path="TNC:", pattern=r"[\$A-Za-z0-9_-]*\.[hH]$")
        print("## found {:d} klartext programs on TNC drive".format(len(h_files)))
        print([f for f in h_files])
        i_files = con.get_file_list(path="TNC:", pattern=r"[\$A-Za-z0-9_-]*\.[iI]$")
        print("## found {:d} ISO programs on TNC drive".format(len(i_files)))

        print("Read spindle tool information")
        t_info = con.spindle_tool_status()
        if t_info is not None:
            print("# direct reading of current tool successful")
            print("# current tool in spindle: {:d}.{:d} '{:s}'".format(t_info.number, t_info.index, t_info.name))
        else:
            print("# direct reading of current tool not supported for this control")


def scope_demo():
    with pyLSV2.LSV2("192.168.56.102", port=19000, timeout=5, safe_mode=False) as con:
        if not con.versions.is_itnc():
            print("the scope functions only work for iTNC controls")
            sys.exit(-1)

        availible_signals = con.read_scope_signals()

        # build list with selected signals
        selected_signals = list()
        selected_signals.append(availible_signals[0])
        selected_signals.append(availible_signals[1])
        selected_signals.append(availible_signals[2])

        print("selected signals:")
        for sig in selected_signals:
            print("# %s" % sig)

        duration = 2
        interval = 3000

        print("reading values for a duration of %d seconds with an interval of %d µs")

        # take readings:
        readings_counter = 0

        for package in con.real_time_readings(selected_signals, duration, interval):
            signal_readings = package.get_data()
            readings_per_signal = len(signal_readings[0].data)
            print("successfully read %d signals with %d values each" % (len(signal_readings), readings_per_signal))

            for i in range(readings_per_signal):
                position_X = signal_readings[0].data[i] * signal_readings[0].factor + signal_readings[0].offset
                position_Y = signal_readings[1].data[i] * signal_readings[1].factor + signal_readings[1].offset
                position_Z = signal_readings[2].data[i] * signal_readings[2].factor + signal_readings[2].offset
                readings_counter += 1

                print(
                    "Count: %d Position X = %.3f mm, Position Y = %.3f, Position Z = %.3f"
                    % (readings_counter, position_X, position_Y, position_Z)
                )

    print("# a total of %d readings were taken" % readings_counter)

    print("# the signal description was updated to:")
    for signal in selected_signals:
        print("##", signal)


if __name__ == "__main__":
    comprehensive_demo()
