#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import string
import time
from pyLSV2_v2 import PrototypeLSV2

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.DEBUG)

    lsv2 = PrototypeLSV2('192.168.56.101', safe_mode=False)

    lsv2.connect()
    lsv2.login(login=PrototypeLSV2.LOGIN_INSPECT)
    lsv2.login(login=PrototypeLSV2.LOGIN_DNC)
    lsv2.login(login=PrototypeLSV2.LOGIN_INSPECT)
    lsv2.login(login=PrototypeLSV2.LOGIN_DIAG)
    lsv2.login(login=PrototypeLSV2.LOGIN_PLCDEBUG)
    lsv2.login(login=PrototypeLSV2.LOGIN_FILETRANSFER)
    lsv2.login(login=PrototypeLSV2.LOGIN_MONITOR)
    lsv2.login(login=PrototypeLSV2.LOGIN_DSP)
    lsv2.login(login=PrototypeLSV2.LOGIN_DNC)
    lsv2.login(login=PrototypeLSV2.LOGIN_SCOPE)
    lsv2.login(login=PrototypeLSV2.LOGIN_FILEPLC, password='807667')

    base_string = 'A_'
    with open('./out.txt', 'a') as fp:
        for first_letter in list(string.ascii_uppercase)[:]:
            for second_letter in list(string.ascii_uppercase)[:]:
                cmd = base_string + first_letter + second_letter
                fp.write(lsv2._test_command(command_string=cmd, payload=None) + '\n')
                time.sleep(0.5)

    lsv2.disconnect()
