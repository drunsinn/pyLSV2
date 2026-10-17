#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collection of topic-based examples for pyLSV2.

Run individual demos via subcommands, for example:
    python -m pyLSV2.scripts.demo basics --address 192.168.56.111
    python -m pyLSV2.scripts.demo machine --address 192.168.56.111
"""

import argparse
import logging
import struct
import sys
import time

import pyLSV2
from pyLSV2 import const as lc
from pyLSV2 import misc as lm
from pyLSV2.const import MemoryType


def add_common_arguments(parser):
    """Add network and logging flags to a demo subcommand."""
    parser.add_argument("address", nargs="?", help="IP address or hostname of the control", type=str)
    parser.add_argument("--address", dest="address_opt", help="IP address or hostname of the control", type=str)
    parser.add_argument("-p", "--port", help="LSV2 port", type=int, default=19000)
    parser.add_argument("-t", "--timeout", help="socket timeout in seconds", type=float, default=5.0)
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


def connect(args, safe_mode: bool = False):
    """Create a configured LSV2 connection for the given demo."""
    if args.address is None:
        args.address = args.address_opt
    if args.address is None:
        raise ValueError("An address must be provided via positional argument or --address")
    return pyLSV2.LSV2(args.address, port=args.port, timeout=args.timeout, safe_mode=safe_mode)


def demo_basics(args):
    """Basic version and connection information."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("Basics:")
        print(f"# Connected to a '{con.versions.control}' running software version '{con.versions.nc_sw}'")
        print(
            "# Version as numeric values base:{:d} type:{:d} version:{:d} service pack:{:d}".format(
                con.versions.nc_sw_base,
                con.versions.nc_sw_type,
                con.versions.nc_sw_version,
                con.versions.nc_sw_service_pack,
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
            print(f"# Time and date: {con.get_remote_datetime()}")

        print("# read error messages, only available on some iTNC530 versions")
        if con.versions.is_itnc():
            if con.versions.nc_sw_base == 340490 and con.versions.nc_sw_version <= 2:
                print("### control is iTNC but does not support this function")
            else:
                error_messages = con.get_error_messages()
                print(f"## Number of currently active error messages: {len(error_messages)}")
                for idx, msg in enumerate(error_messages):
                    print(f"### Error {idx} : {msg}")
        else:
            print("## function 'get_error_messages()' not supported for this control")


def demo_machine(args):
    """Machine state, program state, and overrides."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("Machine:")
        print(f"# axes positions: {con.axes_location()}")

        exec_stat = con.execution_state()
        exec_stat_text = pyLSV2.get_execution_status_text(exec_stat)
        print(f"# execution: {exec_stat} - '{exec_stat_text}'")

        pgm_stat = con.program_status()
        pgm_stat_text = pyLSV2.get_program_status_text(pgm_stat)
        print(f"# program: {pgm_stat} - '{pgm_stat_text}'")

        pgm_stack = con.program_stack()
        if pgm_stack is not None:
            print(f"# selected program: '{pgm_stack.main}'")
            print(f"## currently execution '{pgm_stack.current}' on line {pgm_stack.line_no}")

        ovr_stat = con.override_state()
        if ovr_stat is not None:
            print(
                "# override states: feed {:f}%, rapid {:f}%, spindle {:f}%".format(
                    ovr_stat.feed,
                    ovr_stat.rapid,
                    ovr_stat.spindle,
                )
            )


def demo_rri_parameters(args):
    """Show how to query the R_RI command with the available parameter IDs."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("R_RI parameter examples:")
        print("# The R_RI command expects a two-byte parameter ID from lc.ParRRI")
        print("# Example payload: struct.pack('!H', lc.ParRRI.EXEC_STATE)")

        parameter_examples = [
            (lc.ParRRI.AXIS_CONF_NAMES, "axis configuration names"),
            (lc.ParRRI.AXIS_PHY_NAMES, "axis physical names"),
            (lc.ParRRI.AXIS_LOCATION, "axis location"),
            (lc.ParRRI.EXEC_STATE, "execution state"),
            (lc.ParRRI.SELECTED_PGM, "selected program / current block"),
            (lc.ParRRI.OVERRIDE, "override values"),
            (lc.ParRRI.PGM_STATE, "program state"),
            (lc.ParRRI.FIRST_ERROR, "first error"),
            (lc.ParRRI.NEXT_ERROR, "next error"),
            (lc.ParRRI.NC_UPTIME, "NC uptime"),
            (lc.ParRRI.MACH_UPTIME, "machine uptime"),
            (lc.ParRRI.MACH_RUNTIME, "machine runtime"),
            (lc.ParRRI.SPINDLE_RUNTIME_0, "spindle 0 runtime"),
            (lc.ParRRI.SPINDLE_RUNTIME_1, "spindle 1 runtime"),
            (lc.ParRRI.CURRENT_TOOL, "current tool"),
        ]

        decoders = {
            lc.ParRRI.AXIS_CONF_NAMES: lm.decode_axis_conf_names,
            lc.ParRRI.AXIS_PHY_NAMES: lm.decode_axis_phy_names,
            lc.ParRRI.AXIS_LOCATION: lm.decode_axis_location,
            lc.ParRRI.SELECTED_PGM: lm.decode_stack_info,
            lc.ParRRI.OVERRIDE: lm.decode_override_state,
            lc.ParRRI.FIRST_ERROR: lm.decode_error_message,
            lc.ParRRI.NEXT_ERROR: lm.decode_error_message,
            lc.ParRRI.CURRENT_TOOL: lm.decode_tool_info,
        }

        for parameter, label in parameter_examples:
            if not con.login(login=lc.Login.DNC):
                print(f"## {parameter.name} ({parameter.value}) -> login as DNC failed")
                continue

            payload = struct.pack("!H", parameter.value)
            result = con._send_recive(lc.CMD.R_RI, payload, lc.RSP.S_RI)
            if isinstance(result, (bytearray,)) and len(result) > 0:
                if parameter in decoders:
                    value = decoders[parameter](result)
                    if parameter == lc.ParRRI.CURRENT_TOOL:
                        value = (
                            f"number={value.number}, index={value.index}, axis={value.axis}, "
                            f"length={value.length}, radius={value.radius}"
                        )
                elif parameter == lc.ParRRI.EXEC_STATE:
                    state = lc.ExecState(struct.unpack("!H", result)[0])
                    value = f"{state.name} ({state.value})"
                elif parameter == lc.ParRRI.PGM_STATE:
                    state = lc.PgmState(struct.unpack("!H", result)[0])
                    value = f"{state.name} ({state.value})"
                else:
                    value = result
                print(f"## {parameter.name} ({parameter.value}) -> {label}: {value}")
            else:
                print(f"## {parameter.name} ({parameter.value}) -> {label}: not supported or no data")

        print("# Full parameter list from lc.ParRRI:")
        for member in lc.ParRRI:
            print(f"# - {member.name} = {member.value}")


def demo_plc_memory(args):
    """Read PLC memory values."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("PLC memory:")
        print("# the first 5 entries for some memory types:")
        print(f"## marker: {con.read_plc_memory(0, MemoryType.MARKER, 5)}")
        print(f"## word: {con.read_plc_memory(0, MemoryType.WORD, 5)}")
        print(f"## double word: {con.read_plc_memory(0, MemoryType.DWORD, 5)}")
        print(f"## string: {con.read_plc_memory(0, MemoryType.STRING, 5)}")
        print(f"## input: {con.read_plc_memory(0, MemoryType.INPUT, 5)}")
        print(f"## output: {con.read_plc_memory(0, MemoryType.OUTPUT, 5)}")
        print(f"## input word: {con.read_plc_memory(0, MemoryType.INPUT_WORD, 5)}")
        print(f"## output word: {con.read_plc_memory(0, MemoryType.OUTPUT_WORD, 5)}")
        print(f"## input dword: {con.read_plc_memory(0, MemoryType.INPUT_DWORD, 5)}")
        print(f"## output dword: {con.read_plc_memory(0, MemoryType.OUTPUT_DWORD, 5)}")


def demo_data_paths(args):
    """Read values via data path."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("# data values via data path, only available on some iTNC530")
        if con.versions.is_itnc():
            if con.versions.nc_sw_base == 340490 and con.versions.nc_sw_version <= 2:
                print("### control is iTNC but does not support this function")
            else:
                print(f"## marker 0: {con.read_data_path('/PLC/memory/M/0')}")
                print(f"## marker 1: {con.read_data_path('/PLC/memory/M/1')}")
                print(f"## string 0: {con.read_data_path('/PLC/memory/S/0')}")
                print(f"## word 10908: {con.read_data_path('/PLC/memory/W/10908')}")
        else:
            print("## function 'read_data_path()' not supported for this control")

        print("# table values via data path, only available on some iTNC530")
        if con.versions.is_itnc():
            if con.versions.nc_sw_base == 340490 and con.versions.nc_sw_version <= 2:
                print("### control is iTNC but does not support this function")
            else:
                print("## values from tool table for tool T1:")
                print(f"## DOC column: {con.read_data_path('/TABLE/TOOL/T/1/DOC')}")
                print(f"## L column: {con.read_data_path('/TABLE/TOOL/T/1/L')}")
                print(f"## R column: {con.read_data_path('/TABLE/TOOL/T/1/R')}")
        else:
            print("## function 'read_data_path()' not supported for this control")


def demo_configuration(args):
    """Machine parameters and keyboard interaction."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("Configuration:")
        if con.versions.is_itnc():
            language = con.get_machine_parameter("7230.0")
        else:
            language = con.get_machine_parameter("CfgDisplayLanguage.ncLanguage")
        print(f"# Value of machine parameter for NC language: {language}")

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


def demo_file_access(args):
    """Drive, directory, and file access."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        print("File access:")
        drv_info = con.drive_info()
        print(f"# names of disk drives: {', '.join([drv.name for drv in drv_info])}")
        dir_info = con.directory_info()
        print(f"# current directory is '{dir_info.path}' with {dir_info.free_size} bytes of free drive space")

        dir_content = con.directory_content()
        only_files = [entry for entry in dir_content if not entry.is_directory and not entry.is_drive]
        for file_entry in only_files:
            print(f"## file name: {file_entry.name}, date {file_entry.timestamp}, size {file_entry.size} bytes")

        only_dirs = [entry for entry in dir_content if entry.is_directory and not entry.is_drive]
        for file_entry in only_dirs:
            print(f"## directory name: {file_entry.name}, date {file_entry.timestamp}")

        print("# file search")
        h_files = con.get_file_list(path="TNC:", pattern=r"[\$A-Za-z0-9_-]*\.[hH]$")
        print(f"## found {len(h_files)} klartext programs on TNC drive")
        print([f for f in h_files])

        i_files = con.get_file_list(path="TNC:", pattern=r"[\$A-Za-z0-9_-]*\.[iI]$")
        print(f"## found {len(i_files)} ISO programs on TNC drive")
        print([f for f in i_files])

        print("Read spindle tool information")
        t_info = con.spindle_tool_status()
        if t_info is not None:
            print("# direct reading of current tool successful")
            print(f"# current tool in spindle: {t_info.number}.{t_info.index} '{t_info.name}'")
        else:
            print("# direct reading of current tool not supported for this control")


def demo_scope(args):
    """Read and display scope traces (iTNC only)."""
    logging.basicConfig(level=args.loglevel)
    print(f"Connecting to {args.address}")

    with connect(args, safe_mode=False) as con:
        if not con.versions.is_itnc():
            print("the scope functions only work for iTNC controls")
            sys.exit(-1)

        available_signals = con.read_scope_signals()
        available_signal_names = {f"{signal.channel_name} - {signal.signal_name}": signal for signal in available_signals}

        selected_signals = []
        try:
            selected_signals.append(available_signal_names["s ist - X"])
            selected_signals.append(available_signal_names["s ist - Y"])
            selected_signals.append(available_signal_names["s ist - Z"])
        except Exception as exc:
            print(f"Could not select prepared signals because of the error: {exc}")
            print("The following signals are available on your control:")
            for key in list(available_signal_names.keys()):
                print(key)
            raise SystemExit(1)

        print("selected signals:")
        for sig in selected_signals:
            print(f"# {sig}")

        duration = 2
        interval = 3000
        print(f"reading values for a duration of {duration} seconds with an interval of {interval} µs")

        readings_counter = 0
        for package in con.real_time_readings(selected_signals, duration, interval):
            signal_readings = package.get_data()
            readings_per_signal = len(signal_readings[0].data)
            print(f"successfully read {len(signal_readings)} signals with {readings_per_signal} values each")

            for i in range(readings_per_signal):
                position_x = signal_readings[0].data[i] * signal_readings[0].factor + signal_readings[0].offset
                position_y = signal_readings[1].data[i] * signal_readings[1].factor + signal_readings[1].offset
                position_z = signal_readings[2].data[i] * signal_readings[2].factor + signal_readings[2].offset
                readings_counter += 1
                print(
                    "Count: %d Position X = %.3f mm, Position Y = %.3f, Position Z = %.3f"
                    % (readings_counter, position_x, position_y, position_z)
                )

        print(f"# a total of {readings_counter} readings were taken")
        print("# the signal description was updated to:")
        for signal in selected_signals:
            print("##", signal)


def demo_all(args):
    """Run each demo in sequence for convenience. This is intentionally explicit and not the default."""
    logging.basicConfig(level=args.loglevel)
    for demo_func in (
        demo_basics,
        demo_machine,
        demo_plc_memory,
        demo_data_paths,
        demo_configuration,
        demo_file_access,
        demo_scope,
    ):
        print(f"\n=== Running {demo_func.__name__} ===")
        demo_func(args)


def build_parser():
    """Build the command-line interface with one demo per topic."""
    parser = argparse.ArgumentParser(description="Topic-based pyLSV2 demos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name, handler in (
        ("basics", demo_basics),
        ("machine", demo_machine),
        ("rri", demo_rri_parameters),
        ("plc-memory", demo_plc_memory),
        ("data-path", demo_data_paths),
        ("configuration", demo_configuration),
        ("file-access", demo_file_access),
        ("scope", demo_scope),
        ("all", demo_all),
    ):
        subparser = subparsers.add_parser(command_name, help=handler.__doc__)
        add_common_arguments(subparser)
        subparser.set_defaults(handler=handler)

    return parser


def main(argv=None):
    """CLI entry point for the topic-based demo script."""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.handler(args)


def main_scope(argv=None):
    """Convenience entry point that runs the scope demo directly."""
    args = ["scope"]
    if argv is None:
        args.extend(sys.argv[1:])
    else:
        args.extend(argv)
    main(args)


if __name__ == "__main__":
    main()
