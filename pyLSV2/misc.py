#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""misc helper functions for pyLSV2"""
import struct


def decode_system_parameters(result_set):
    """decode the result system parameter query

    :param tuple result_set: bytes returnde by the system parameter query command R_PR
    :returns: dictionary with system parameter values
    :rtype: dict
    """
    message_length = len(result_set)
    info_list = list()
    # as per comment in eclipse plugin, there might be a difference between a programming station and a real machine
    if message_length == 120:
        info_list = struct.unpack('!14L8B8L2BH4B2L2HL', result_set)
    elif message_length == 124:
        info_list = struct.unpack('!14L8B8L2BH4B2L2HLL', result_set)
    else:
        raise ValueError('unexpected length {} of message content {}'.format(message_length, result_set))
    sys_par = dict()
    sys_par['Marker_Start'] = info_list[0]
    sys_par['Markers'] = info_list[1]
    sys_par['Input_Start'] = info_list[2]
    sys_par['Inputs'] = info_list[3]
    sys_par['Output_Start'] = info_list[4]
    sys_par['Outputs'] = info_list[5]
    sys_par['Counter_Start'] = info_list[6]
    sys_par['Counters'] = info_list[7]
    sys_par['Timer_Start'] = info_list[8]
    sys_par['Timers'] = info_list[9]
    sys_par['Word_Start'] = info_list[10]
    sys_par['Words'] = info_list[11]
    sys_par['String_Start'] = info_list[12]
    sys_par['Strings'] = info_list[13]
    sys_par['String_Length'] = info_list[14]
    sys_par['Input_Word_Start'] = info_list[22]
    sys_par['Input Words'] = info_list[23]
    sys_par['Output_Word_Start'] = info_list[24]
    sys_par['Output_Words'] = info_list[25]
    sys_par['LSV2_Version'] = info_list[30]
    sys_par['LSV2_Version_Flags'] = info_list[31]
    sys_par['Max_Block_Length'] = info_list[32]
    sys_par['HDH_Bin_Version'] = info_list[33]
    sys_par['HDH_Bin_Revision'] = info_list[34]
    sys_par['ISO_Bin_Version'] = info_list[35]
    sys_par['ISO_Bin_Revision'] = info_list[36]
    sys_par['HardwareVersion'] = info_list[37]
    sys_par['LSV2_Version_Flags_Ex'] = info_list[38]
    sys_par['Max_Trace_Line'] = info_list[39]
    sys_par['Scope_Channels'] = info_list[40]
    sys_par['PW_Encryption_Key'] = info_list[41]
    return sys_par
