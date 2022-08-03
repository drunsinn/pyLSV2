#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""misc helper functions for pyLSV2"""
import struct
from datetime import datetime
from pathlib import Path
from typing import Union

from . import dat_cls as ld
from .const import BIN_FILES, PATH_SEP, ControlType


def decode_system_parameters(result_set: bytearray) -> ld.SystemParameters:
    """
    Decode the result system parameter query

    :param result_set: bytes returned by the system parameter query command R_PR
    """
    message_length = len(result_set)
    info_list = []
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
    sys_par = ld.SystemParameters()
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
) -> ld.FileEntry:
    """
    Decode result from file system entry

    :param result_set: bytes returned by the system parameter query command R_FI or CR_DR
    """

    """
    according to documentation an LSV version 1 this should be:
    ATTR_DISPLAY 0x01
    ATTR_CHANGABLE 0x02
    ATTR_HIGHLITED 0x04
    ATTR_HIDE 0x08
    ATTR_DIR 0x10
    ATTR_PROTECT 0x20
    
    another document has:
    ATTR_DISPLAY 0x01
    ATTR_CHANGEABLE 0x02
    ATTR_HIGHLIGHTED 0x08 (this might be an error in the documentation!)
    ATTR_HIDE 0x08
    ATTR_DIR 0x10
    ATTR_SUBDIR 0x20
    ATTR_PROTECT 0x40
    ATTR_SELECTED 0x80
    """

    # flag_display = 0x01
    flag_changable = 0x02
    # flag_highlighted = 0x04
    flag_hidden = 0x08
    flag_dir = 0x10
    flag_subdir = 0x20
    flag_protected = 0x40
    # flag_selected = 0x80

    # if control_type in (ControlType.MILL_OLD,ControlType.LATHE_OLD):
    #   flag_highlight = 0x04

    fi = ld.FileEntry
    fi.size = struct.unpack("!L", data_set[:4])[0]
    fi.timestamp = datetime.fromtimestamp(
        struct.unpack("!L", data_set[4:8])[0])

    fi.attributes = struct.unpack("!L", data_set[8:12])[0]

    fi.is_changable = bool(fi.attributes & flag_changable)
    fi.is_drive = bool(fi.attributes & flag_dir)
    fi.is_directory = bool(fi.attributes & flag_subdir)
    fi.is_protected = bool(fi.attributes & flag_protected)
    fi.is_hidden = bool(fi.attributes & flag_hidden)

    fi.name = ba_to_ustr(data_set[12:]).replace("/", PATH_SEP)
    return fi


def decode_directory_info(data_set: bytearray) -> ld.DirectoryEntry:
    """
    Decode result from directory entry

    :param result_set: bytes returned by the system parameter query command R_DI
    """
    di = ld.DirectoryEntry()
    di.free_size = struct.unpack("!L", data_set[:4])[0]

    attribute_list = []
    for i in range(4, len(data_set[4:132]), 4):
        attr = ba_to_ustr(data_set[i: i + 4])
        if len(attr) > 0:
            attribute_list.append(attr)
    di.dir_attributes = attribute_list

    di.attributes = struct.unpack("!32B", data_set[132:164])
    di.path = ba_to_ustr(data_set[164:]).replace("/", PATH_SEP)

    return di


def decode_tool_info(data_set: bytearray) -> ld.ToolInformation:
    """
    Decode result from tool info

    :param result_set: bytes returned by the system parameter query command R_RI for tool info
    """
    ti = ld.ToolInformation()
    ti.number = struct.unpack("!L", data_set[0:4])[0]
    ti.index = struct.unpack("!H", data_set[4:6])[0]
    ti.axis = {0: "X", 1: "Y", 2: "Z"}.get(
        struct.unpack("!H", data_set[6:8])[0], "unknown"
    )
    if len(data_set) > 8:
        ti.length = struct.unpack("<d", data_set[8:16])[0]
        ti.radius = struct.unpack("<d", data_set[16:24])[0]
    return ti


def decode_override_state(data_set: bytearray) -> ld.OverrideState:
    """
    Decode result from override info

    :param result_set: bytes returned by the system parameter query command R_RI for override info
    """
    oi = ld.OverrideState()
    oi.feed = struct.unpack("!L", data_set[0:4])[0] / 100
    oi.spindel = struct.unpack("!L", data_set[4:8])[0] / 100
    oi.rapid = struct.unpack("!L", data_set[8:12])[0] / 100
    return oi


def decode_error_message(data_set: bytearray) -> ld.LSV2ErrorMessage:
    """
    Decode result from reading error messages

    :param result_set: bytes returned by the system parameter query command R_RI for first and next error
    """
    ei = ld.LSV2ErrorMessage()
    ei.e_class = struct.unpack("!H", data_set[0:2])[0]
    ei.e_group = struct.unpack("!H", data_set[2:4])[0]
    ei.e_number = struct.unpack("!l", data_set[4:8])[0]
    ei.e_text = ba_to_ustr(data_set[8:])
    ei.dnc = True
    return ei


def decode_stack_info(data_set: bytearray) -> ld.StackState:
    """
    Decode result from reading stack information

    :param data_set: bytes returned from query
    """
    ss = ld.StackState()
    ss.current_line = struct.unpack("!L", data_set[:4])[0]
    ss.main_pgm = ba_to_ustr(data_set[4:].split(b"\x00")[0])
    ss.current_pgm = ba_to_ustr(data_set[4:].split(b"\x00")[1])
    return ss


def is_file_binary(file_name: Union[str, Path]) -> bool:
    """
    Check if file is expected to be binary by comparing with known expentions.
    Returns ``True`` if file matches know binary file type
    """
    for bin_type in BIN_FILES:
        if isinstance(file_name, Path):
            if file_name.suffix == bin_type:
                return True
        elif file_name.endswith(bin_type):
            return True
    return False


def ba_to_ustr(bytes_to_convert: bytearray) -> str:
    """
    convert a bytearry of characters to unicode string

    :param bytes_to_convert: bytes to convert to unicode string
    """
    return bytes_to_convert.decode("latin1").strip("\x00").strip()
