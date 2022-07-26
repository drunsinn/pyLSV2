#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""misc helper functions for pyLSV2"""
import struct
from datetime import datetime
from pathlib import Path
from typing import Union

from .const import PATH_SEP, ControlType, BIN_FILES
from .dat_cls import SystemParameters, OverrideState, LSV2ErrorMessage, StackState


def decode_system_parameters(result_set: bytearray) -> SystemParameters:
    """decode the result system parameter query

    :param bytearray result_set: bytes returned by the system parameter query command R_PR
    :returns: dictionary with system parameter values
    :rtype: dict
    """
    message_length = len(result_set)
    info_list = list()
    if message_length == 120:
        info_list = struct.unpack("!14L8B8L2BH4B2L2HL", result_set)
    elif message_length == 124:
        info_list = struct.unpack("!14L8B8L2BH4B2L2HLL", result_set)
    else:
        raise ValueError(
            "unexpected length {} of message content {}".format(
                message_length, result_set
            )
        )
    sys_par = SystemParameters()
    sys_par.markers_start_address = info_list[0]
    sys_par.number_of_markers = info_list[1]

    sys_par.inputs_start_address = info_list[2]
    sys_par.number_of_inputs = info_list[3]

    sys_par.outputs_start_address = info_list[4]
    sys_par.number_of_outputs = info_list[5]

    sys_par.counters_start_address = info_list[6]
    sys_par.number_of_counters = info_list[7]

    sys_par.timers_start_address = info_list[8]
    sys_par.number_of_timers = info_list[9]

    sys_par.words_start_address = info_list[10]
    sys_par.number_of_words = info_list[11]

    sys_par.strings_start_address = info_list[12]
    sys_par.number_of_strings = info_list[13]
    sys_par.max_string_lenght = info_list[14]

    sys_par.input_words_start_address = info_list[22]
    sys_par.number_of_input_words = info_list[23]

    sys_par.output_words_start_address = info_list[24]
    sys_par.number_of_output_words = info_list[25]

    sys_par.lsv2_version = info_list[30]
    sys_par.lsv2_version_flags = info_list[31]
    sys_par.lsv2_version_flags_ex = info_list[38]

    sys_par.max_block_length = info_list[32]

    sys_par.bin_version = info_list[33]
    sys_par.bin_revision = info_list[34]

    sys_par.iso_version = info_list[35]
    sys_par.iso_revision = info_list[36]

    sys_par.hardware_version = info_list[37]

    sys_par.max_trace_line = info_list[39]
    sys_par.number_of_scope_channels = info_list[40]
    sys_par.password_encryption_key = info_list[41]
    return sys_par


def decode_file_system_info(
    data_set: bytearray, control_type: ControlType = ControlType.UNKNOWN
):
    """decode result from file system entry

    :param bytearray result_set: bytes returned by the system parameter query command R_FI or CR_DR
    :returns: dictionary with file system entry parameters
    :rtype: dict
    """
    flag_is_protected = 0x08
    if control_type in (
        ControlType.UNKNOWN,
        ControlType.MILL_NEW,
        ControlType.LATHE_NEW,
    ):
        flag_is_dir = 0x20
    else:
        flag_is_dir = 0x40

    file_info = dict()
    file_info["Size"] = struct.unpack("!L", data_set[:4])[0]
    file_info["Timestamp"] = datetime.fromtimestamp(
        struct.unpack("!L", data_set[4:8])[0]
    )

    attributes = struct.unpack("!L", data_set[8:12])[0]

    file_info["Attributes"] = attributes
    file_info["is_file"] = False
    file_info["is_directory"] = False

    if bool(attributes & flag_is_dir):
        file_info["is_directory"] = True
    else:
        file_info["is_file"] = True

    file_info["is_write_protected"] = bool(attributes & flag_is_protected)

    file_info["Name"] = ba_to_ustr(data_set[12:]).replace("/", PATH_SEP)

    return file_info


def decode_directory_info(data_set: bytearray):
    """decode result from directory entry

    :param bytearray result_set: bytes returned by the system parameter query command R_DI
    :returns: dictionary with file system entry parameters
    :rtype: dict
    """
    dir_info = dict()
    dir_info["Free Size"] = struct.unpack("!L", data_set[:4])[0]
    attribute_list = list()
    for i in range(4, len(data_set[4:132]), 4):
        attr = ba_to_ustr(data_set[i: i + 4])
        if len(attr) > 0:
            attribute_list.append(attr)
    dir_info["Dir_Attributs"] = attribute_list

    dir_info["Attributes"] = struct.unpack("!32B", data_set[132:164])

    dir_info["Path"] = ba_to_ustr(data_set[164:]).replace("/", PATH_SEP)

    return dir_info


def decode_tool_information(data_set: bytearray):
    """decode result from tool info

    :param bytearray result_set: bytes returned by the system parameter query command R_RI for tool info
    :returns: dictionary with tool info values
    :rtype: dict
    """
    tool_info = dict()
    tool_info["Number"] = struct.unpack("!L", data_set[0:4])[0]
    tool_info["Index"] = struct.unpack("!H", data_set[4:6])[0]
    tool_info["Axis"] = {0: "X", 1: "Y", 2: "Z"}.get(
        struct.unpack("!H", data_set[6:8])[0], "unknown"
    )
    if len(data_set) > 8:
        tool_info["Length"] = struct.unpack("<d", data_set[8:16])[0]
        tool_info["Radius"] = struct.unpack("<d", data_set[16:24])[0]
    else:
        tool_info["Length"] = None
        tool_info["Radius"] = None
    return tool_info


def decode_override_state(data_set: bytearray) -> OverrideState:
    """decode result from override info

    :param bytearray result_set: bytes returned by the system parameter query command R_RI for
                             override info
    :returns: dictionary with override info values
    :rtype: dict
    """
    oi = OverrideState()
    oi.feed = struct.unpack("!L", data_set[0:4])[0] / 100
    oi.spindel = struct.unpack("!L", data_set[4:8])[0] / 100
    oi.rapid = struct.unpack("!L", data_set[8:12])[0] / 100
    return oi


def decode_error_message(data_set: bytearray) -> LSV2ErrorMessage:
    """decode result from reading error messages

    :param bytearray result_set: bytes returned by the system parameter query command R_RI for
                             first and next error
    :returns: error message values
    :rtype: 
    """
    ei = LSV2ErrorMessage()
    ei.e_class = struct.unpack("!H", data_set[0:2])[0]
    ei.e_group = struct.unpack("!H", data_set[2:4])[0]
    ei.e_number = struct.unpack("!l", data_set[4:8])[0]
    ei.e_text = ba_to_ustr(data_set[8:])
    ei.dnc = True
    return ei


def decode_stack_info(data_set: bytearray) -> StackState:
    ss = StackState()
    ss.current_line = struct.unpack("!L", data_set[:4])[0]
    ss.main_pgm = ba_to_ustr(data_set[4:].split(b"\x00")[0])
    ss.current_pgm = ba_to_ustr(data_set[4:].split(b"\x00")[1])
    return ss


def is_file_binary(file_name: Union[str, Path]) -> bool:
    """Check if file is expected to be binary by comparing with known expentions.

    :param file_name: name of the file to check
    :returns: True if file matches know binary file type
    :rtype: bool
    """
    for bin_type in BIN_FILES:
        if isinstance(file_name, Path):
            if file_name.suffix == bin_type:
                return True
        elif file_name.endswith(bin_type):
            return True
    return False


def ba_to_ustr(bytes_to_convert: bytearray) -> str:
    """convert a bytearry of characters to unicode string"""
    return bytes_to_convert.decode("latin1").strip("\x00").strip()
