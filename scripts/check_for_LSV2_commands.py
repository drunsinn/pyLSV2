#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import string
import time
import struct
import pyLSV2


def test_command(lsv2, command_string, payload=None):
    """check commands for validity"""
    response, content = lsv2._llcom.telegram(
        command_string, payload, buffer_size=lsv2._buffer_size)
    if content is None:
        response_length = -1
    else:
        response_length = len(content)
    if response in lsv2.RESPONSE_T_ER:
        if len(content) == 2:
            byte_1, byte_2, = struct.unpack('!BB', content)
            error_text = lsv2.get_error_text(byte_1, byte_2)
        else:
            error_text = 'Unknown Error Number {}'.format(content)
    else:
        error_text = 'NONE'
    return 'sent {} payload {} received {} message_length {} content {} error text : {}'.format(command_string, payload, response, response_length, content, error_text)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.ERROR)
    
    lsv2 = pyLSV2.LSV2('192.168.56.103', safe_mode=False)

    lsv2.connect()
    lsv2.login(login=pyLSV2.LOGIN_INSPECT)
    lsv2.login(login=pyLSV2.LOGIN_DNC)
    lsv2.login(login=pyLSV2.LOGIN_INSPECT)
    lsv2.login(login=pyLSV2.LOGIN_DIAG)
    lsv2.login(login=pyLSV2.LOGIN_PLCDEBUG)
    lsv2.login(login=pyLSV2.LOGIN_FILETRANSFER)
    lsv2.login(login=pyLSV2.LOGIN_MONITOR)
    lsv2.login(login=pyLSV2.LOGIN_DSP)
    lsv2.login(login=pyLSV2.LOGIN_DNC)
    lsv2.login(login=pyLSV2.LOGIN_SCOPE)
    lsv2.login(login=pyLSV2.LOGIN_FILEPLC, password='<PLC_PASSWORD>')

    # base_string = 'A_'
    # with open('./out.txt', 'a') as fp:
    #     for first_letter in list(string.ascii_uppercase)[:]:
    #         for second_letter in list(string.ascii_uppercase)[:]:
    #             cmd = base_string + first_letter + second_letter
    #             fp.write(lsv2._test_command(command_string=cmd, payload=None) + '\n')
    #             time.sleep(0.5)

    with open('./out.txt', 'a') as fp:
        for i in range (0, 0xFFFFFFFF):
            fp.write(test_command(lsv2, command_string='R_MB', payload=struct.pack('!L', i)) + '\n')


    lsv2.disconnect()
