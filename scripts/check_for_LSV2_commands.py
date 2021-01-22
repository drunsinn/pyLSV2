#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import string
import time
import struct
from pyLSV2 import LSV2

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.ERROR)
    
    lsv2 = LSV2('192.168.56.103', safe_mode=False)

    lsv2.connect()
    lsv2.login(login=LSV2.LOGIN_INSPECT)
    lsv2.login(login=LSV2.LOGIN_DNC)
    lsv2.login(login=LSV2.LOGIN_INSPECT)
    lsv2.login(login=LSV2.LOGIN_DIAG)
    lsv2.login(login=LSV2.LOGIN_PLCDEBUG)
    lsv2.login(login=LSV2.LOGIN_FILETRANSFER)
    lsv2.login(login=LSV2.LOGIN_MONITOR)
    lsv2.login(login=LSV2.LOGIN_DSP)
    lsv2.login(login=LSV2.LOGIN_DNC)
    lsv2.login(login=LSV2.LOGIN_SCOPE)
    lsv2.login(login=LSV2.LOGIN_FILEPLC, password='807667')

    # base_string = 'A_'
    # with open('./out.txt', 'a') as fp:
    #     for first_letter in list(string.ascii_uppercase)[:]:
    #         for second_letter in list(string.ascii_uppercase)[:]:
    #             cmd = base_string + first_letter + second_letter
    #             fp.write(lsv2._test_command(command_string=cmd, payload=None) + '\n')
    #             time.sleep(0.5)

    with open('./out.txt', 'a') as fp:
        for i in range (0, 0xFFFFFFFF):
            fp.write(lsv2._test_command(command_string='R_MB', payload=struct.pack('!L', i)) + '\n')


    lsv2.disconnect()
