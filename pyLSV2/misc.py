#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""misc helper functions for pyLSV2"""
import struct
from datetime import datetime

from .const import ControlType


def decode_system_parameters(result_set):
    """decode the result system parameter query

    :param tuple result_set: bytes returned by the system parameter query command R_PR
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
    sys_par = dict()
    sys_par["Marker_Start"] = info_list[0]
    sys_par["Markers"] = info_list[1]
    sys_par["Input_Start"] = info_list[2]
    sys_par["Inputs"] = info_list[3]
    sys_par["Output_Start"] = info_list[4]
    sys_par["Outputs"] = info_list[5]
    sys_par["Counter_Start"] = info_list[6]
    sys_par["Counters"] = info_list[7]
    sys_par["Timer_Start"] = info_list[8]
    sys_par["Timers"] = info_list[9]
    sys_par["Word_Start"] = info_list[10]
    sys_par["Words"] = info_list[11]
    sys_par["String_Start"] = info_list[12]
    sys_par["Strings"] = info_list[13]
    sys_par["String_Length"] = info_list[14]
    sys_par["Input_Word_Start"] = info_list[22]
    sys_par["Input Words"] = info_list[23]
    sys_par["Output_Word_Start"] = info_list[24]
    sys_par["Output_Words"] = info_list[25]
    sys_par["LSV2_Version"] = info_list[30]
    sys_par["LSV2_Version_Flags"] = info_list[31]
    sys_par["Max_Block_Length"] = info_list[32]
    sys_par["HDH_Bin_Version"] = info_list[33]
    sys_par["HDH_Bin_Revision"] = info_list[34]
    sys_par["ISO_Bin_Version"] = info_list[35]
    sys_par["ISO_Bin_Revision"] = info_list[36]
    sys_par["HardwareVersion"] = info_list[37]
    sys_par["LSV2_Version_Flags_Ex"] = info_list[38]
    sys_par["Max_Trace_Line"] = info_list[39]
    sys_par["Scope_Channels"] = info_list[40]
    sys_par["PW_Encryption_Key"] = info_list[41]
    return sys_par


def decode_file_system_info(data_set, control_type=ControlType.UNKNOWN):
    """decode result from file system entry

    :param tuple result_set: bytes returned by the system parameter query command R_FI or CR_DR
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

    file_info["Name"] = data_set[12:].decode("latin1").strip("\x00").replace("\\", "/")

    return file_info


def decode_directory_info(data_set):
    """decode result from directory entry

    :param tuple result_set: bytes returned by the system parameter query command R_DI
    :returns: dictionary with file system entry parameters
    :rtype: dict
    """
    dir_info = dict()
    dir_info["Free Size"] = struct.unpack("!L", data_set[:4])[0]
    attribute_list = list()
    for i in range(4, len(data_set[4:132]), 4):
        attr = data_set[i : i + 4].decode("latin1").strip("\x00")
        if len(attr) > 0:
            attribute_list.append(attr)
    dir_info["Dir_Attributs"] = attribute_list

    dir_info["Attributes"] = struct.unpack("!32B", data_set[132:164])

    dir_info["Path"] = data_set[164:].decode("latin1").strip("\x00").replace("\\", "/")

    return dir_info


def decode_tool_information(data_set):
    """decode result from tool info

    :param tuple result_set: bytes returned by the system parameter query command R_RI for tool info
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


def decode_override_information(data_set):
    """decode result from override info

    :param tuple result_set: bytes returned by the system parameter query command R_RI for
                             override info
    :returns: dictionary with override info values
    :rtype: dict
    """
    override_info = dict()
    override_info["Feed_override"] = struct.unpack("!L", data_set[0:4])[0] / 100
    override_info["Speed_override"] = struct.unpack("!L", data_set[4:8])[0] / 100
    override_info["Rapid_override"] = struct.unpack("!L", data_set[8:12])[0] / 100

    return override_info


def decode_error_message(data_set):
    """decode result from reading error messages

    :param tuple result_set: bytes returned by the system parameter query command R_RI for
                             first and next error
    :returns: dictionary with error message values
    :rtype: dict
    """
    error_info = dict()
    error_info["Class"] = struct.unpack("!H", data_set[0:2])[0]
    error_info["Group"] = struct.unpack("!H", data_set[2:4])[0]
    error_info["Number"] = struct.unpack("!l", data_set[4:8])[0]
    error_info["Text"] = data_set[8:].decode("latin1").strip("\x00")
    return error_info
