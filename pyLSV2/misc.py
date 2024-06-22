#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""misc helper functions for pyLSV2"""
import struct
import re
from datetime import datetime
from pathlib import Path
from typing import Union, List, Dict

from . import dat_cls as ld
from .const import BIN_FILES, PATH_SEP, ControlType, MemoryType
from .err import LSV2DataException


def decode_system_parameters(result_set: bytearray) -> ld.SystemParameters:
    """
    Decode the result system parameter query

    :param result_set: bytes returned by the system parameter query command R_PR,

    :raises LSV2DataException: Error during parsing of data values
    """
    message_length = len(result_set)
    info_list = []
    if message_length == 120:
        info_list = struct.unpack("!14L8B8L2BH4B2L2HL", result_set)
    elif message_length == 124:
        info_list = struct.unpack("!14L8B8L2BH4B2L2HLL", result_set)
    else:
        raise LSV2DataException("unexpected length %s of message content %s" % (message_length, result_set))
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


def decode_system_information(data_set: bytearray) -> Union[bool, int]:
    """
    Decode the result system information query
    :param result_set: bytes returned by the signal description query command R_OC
    :raises LSV2DataException: Error during parsing of data values
    """
    if len(data_set) != 8:
        raise LSV2DataException("unexpected length of system information package")

    data_type = struct.unpack("!L", data_set[:4])[0]

    if data_type == 1:
        return struct.unpack("!xxx?", data_set[4:])[0]

    if data_type == 2:
        return struct.unpack("!L", data_set[4:])[0]

    raise LSV2DataException("unexpected value for data type of system information")


def decode_file_system_info(data_set: bytearray, control_type: ControlType = ControlType.UNKNOWN) -> ld.FileEntry:
    """
    Decode result from file system entry

    :param result_set: bytes returned by the system parameter query command R_FI or CR_DR
    """

    if control_type in (ControlType.MILL_OLD, ControlType.LATHE_OLD):
        # print("select old")
        # according to documentation an LSV version 1 this should be:
        # flag_display = 0x01
        flag_changable = 0x02
        # flag_highlighted = 0x04
        flag_hidden = 0x08
        flag_drive = None
        flag_subdir = 0x40
        flag_protected = 0x20
        flag_selected = None
    else:
        # another newer document has
        # flag_display = 0x01
        flag_changable = 0x02
        # flag_highlighted = 0x04 # was 0x08, this might be an error in the documentation!
        flag_hidden = 0x08
        flag_drive = 0x10
        flag_subdir = 0x20
        flag_protected = 0x40
        flag_selected = 0x80

    file_entry = ld.FileEntry()
    file_entry.size = struct.unpack("!L", data_set[:4])[0]
    file_entry.timestamp = datetime.fromtimestamp(struct.unpack("!L", data_set[4:8])[0])

    file_entry.attributes = struct.unpack("!L", data_set[8:12])[0]

    file_entry.is_changable = (file_entry.attributes & flag_changable) != 0

    if flag_drive is not None:
        file_entry.is_drive = (file_entry.attributes & flag_drive) != 0

    file_entry.is_directory = (file_entry.attributes & flag_subdir) != 0

    file_entry.is_protected = (file_entry.attributes & flag_protected) != 0
    file_entry.is_hidden = (file_entry.attributes & flag_hidden) != 0

    if flag_selected is not None:
        file_entry.is_selected = (file_entry.attributes & flag_selected) != 0

    file_entry.name = ba_to_ustr(data_set[12:]).replace("/", PATH_SEP)

    return file_entry


def decode_drive_info(data_set: bytearray) -> List[ld.DriveEntry]:
    """
    Split and decode result from drive info

    :param result_set: bytes returned by the system parameter query command R_DR mode 'DRIVE'
    """
    offset = 0
    fixed_length = 15
    drive_entries: List[ld.DriveEntry] = []
    while (offset + fixed_length + 1) < len(data_set):
        drive_entry = ld.DriveEntry()
        drive_entry.size = struct.unpack("!L", data_set[offset : offset + 4])[0]
        drive_entry.timestamp = decode_timestamp(data_set[offset + 4 : offset + 8])
        drive_entry.attributes = data_set[offset + 8 : offset + 12]
        if chr(data_set[offset + fixed_length]) == ":":
            drive_entry.name = ba_to_ustr(data_set[offset + 12 : offset + 17])
            offset += fixed_length + 2
        else:
            drive_entry.name = ba_to_ustr(data_set[offset + 12 : offset + 19])
            offset += fixed_length + 2

        drive_entries.append(drive_entry)

    return drive_entries


def decode_directory_info(data_set: bytearray) -> ld.DirectoryEntry:
    """
    Decode result from directory entry

    :param result_set: bytes returned by the system parameter query command R_DI
    """
    dir_entry = ld.DirectoryEntry()
    dir_entry.free_size = struct.unpack("!L", data_set[:4])[0]

    attribute_list: List[str] = []
    for i in range(4, len(data_set[4:132]), 4):
        attr = ba_to_ustr(data_set[i : i + 4])
        if len(attr) > 0:
            attribute_list.append(attr)
    dir_entry.dir_attributes = attribute_list

    dir_entry.attributes = bytearray(struct.unpack("!32B", data_set[132:164]))
    dir_entry.path = ba_to_ustr(data_set[164:]).replace("/", PATH_SEP)

    return dir_entry


def decode_tool_info(data_set: bytearray) -> ld.ToolInformation:
    """
    Decode result from tool info

    :param result_set: bytes returned by the system parameter query command R_RI for tool info
    """
    tool_info = ld.ToolInformation()
    tool_info.number = struct.unpack("!L", data_set[0:4])[0]
    tool_info.index = struct.unpack("!H", data_set[4:6])[0]
    tool_info.axis = {0: "X", 1: "Y", 2: "Z"}.get(struct.unpack("!H", data_set[6:8])[0], "unknown")
    if len(data_set) > 8:
        tool_info.length = struct.unpack("<d", data_set[8:16])[0]
        tool_info.radius = struct.unpack("<d", data_set[16:24])[0]
    return tool_info


def decode_override_state(data_set: bytearray) -> ld.OverrideState:
    """
    Decode result from override info

    :param result_set: bytes returned by the system parameter query command R_RI for override info
    """
    ovr_state = ld.OverrideState()
    ovr_state.feed = struct.unpack("!L", data_set[0:4])[0] / 100
    ovr_state.spindle = struct.unpack("!L", data_set[4:8])[0] / 100
    ovr_state.rapid = struct.unpack("!L", data_set[8:12])[0] / 100
    return ovr_state


def decode_error_message(data_set: bytearray) -> ld.NCErrorMessage:
    """
    Decode result from reading error messages

    :param result_set: bytes returned by the system parameter query command R_RI for first and next error
    """
    err_msg = ld.NCErrorMessage()
    err_msg.e_class = struct.unpack("!H", data_set[0:2])[0]
    err_msg.e_group = struct.unpack("!H", data_set[2:4])[0]
    err_msg.e_number = struct.unpack("!l", data_set[4:8])[0]
    err_msg.e_text = ba_to_ustr(data_set[8:])
    err_msg.dnc = True
    return err_msg


def decode_stack_info(data_set: bytearray) -> ld.StackState:
    """
    Decode result from reading stack information

    :param data_set: bytes returned from query
    """
    stack = ld.StackState()
    stack.line_no = struct.unpack("!L", data_set[:4])[0]
    stack.main = ba_to_ustr(data_set[4:].split(b"\x00")[0])
    stack.current = ba_to_ustr(data_set[4:].split(b"\x00")[1])
    return stack


def decode_axis_location(data_set: bytearray) -> Dict[str, float]:
    """
    Decode result from reading axis position
    Returns dictionary with key = axis name, value = position

    :param data_set: bytes returned from query

    :raises LSV2DataException: Error during parsing of data values
    """
    # unknown = result[0:1] # <- ???
    number_of_axes = int(struct.unpack("!b", data_set[1:2])[0])

    split_list: List[str] = []
    start = 2
    for i, byte in enumerate(data_set[start:]):
        if byte == 0x00:
            value = data_set[start : i + 3]
            split_list.append(ba_to_ustr(value))
            start = i + 3

    if len(split_list) != (2 * number_of_axes):
        raise LSV2DataException("error while parsing axis data: %s" % data_set)

    axes_values: Dict[str, float] = {}
    for i in range(number_of_axes):
        axis_name = str(split_list[i + number_of_axes])
        axes_values[axis_name] = float(split_list[i])

    return axes_values


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
    return bytes_to_convert.decode("latin1").strip("\x00").rstrip()


def ustr_to_ba(str_to_convert: str) -> bytearray:
    """
    convert a string to a byte array with string termination

    :param str_to_convert: string that should be converted to byte array
    """
    str_bytes = bytearray(map(ord, str(str_to_convert)))
    str_bytes.append(0x00)
    return str_bytes


def decode_timestamp(data_set: bytearray) -> datetime:
    """
    Decode result from reading the time and date with R_DT
    Returns datetime

    :param data_set: bytes returned from query
    """
    timestamp = struct.unpack("!L", data_set[0:4])[0]
    return datetime.fromtimestamp(timestamp)


def decode_plc_memory_address(address: str):
    """
    Decode memory address location from the format used by the plc program to
    sequential representation.
    """
    val_num = None
    val_type = None
    if result := re.fullmatch(r"(?P<m_type>[MBWDSIO])(?P<s_type>[WD])?(?P<num>\d+)", address):
        m_type = result.group("m_type")
        s_type = result.group("s_type")
        num = int(result.group("num"))
        val_num = num

        if m_type == "M" and s_type is None:
            val_type = MemoryType.MARKER
        elif m_type == "B" and s_type is None:
            val_type = MemoryType.BYTE
        elif m_type == "W" and s_type is None:
            val_num = int(val_num / 2)
            val_type = MemoryType.WORD
        elif m_type == "D" and s_type is None:
            val_num = int(val_num / 4)
            val_type = MemoryType.DWORD
        elif m_type == "I":
            if s_type is None:
                val_type = MemoryType.INPUT
            elif s_type == "W":
                val_num = int(val_num / 2)
                val_type = MemoryType.INPUT_WORD
            elif s_type == "D":
                val_num = int(val_num / 4)
                val_type = MemoryType.INPUT_DWORD
        elif m_type == "O":
            if s_type is None:
                val_type = MemoryType.OUTPUT
            elif s_type == "W":
                val_num = int(val_num / 2)
                val_type = MemoryType.OUTPUT_WORD
            elif s_type == "D":
                val_num = int(val_num / 4)
                val_type = MemoryType.OUTPUT_DWORD
        elif m_type == "S" and s_type is None:
            val_type = MemoryType.STRING

    return val_type, val_num
