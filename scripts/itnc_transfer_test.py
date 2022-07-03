#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sys

import time
import pyLSV2
from pyLSV2.const import CMD, RSP, ParCCC

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    address = "192.168.56.101"
    if len(sys.argv) > 1:
        address = sys.argv[1]
    print("Connecting to {}".format(address))

    logging.basicConfig(level=logging.DEBUG)

    con = pyLSV2.LSV2(address, port=19000, timeout=5, safe_mode=False)

    con._llcom.connect()

    # login INSPECT
    payload = bytearray()
    payload.extend(map(ord, "INSPECT"))
    payload.append(0x00)
    result = con._send_recive(command="A_LG", expected_response="T_OK", payload=payload)

    # read info
    result = con._send_recive(command="R_VR", expected_response="S_VR", payload=None)

    # read parameters
    result = con._send_recive(command="R_PR", expected_response="S_PR", payload=None)

    # set system par 0x00 0x03 -> set buffer 1024
    payload = bytearray()
    payload.append(0x00)
    payload.append(0x03)
    result = con._send_recive(command="C_CC", expected_response="T_OK", payload=payload)
    con._buffer_size = 1024

    # set system par 0x00 0x06  -> set buffer 3075
    payload = bytearray()
    payload.append(0x00)
    payload.append(0x06)
    result = con._send_recive(command="C_CC", expected_response="T_OK", payload=payload)
    con._buffer_size = 3075

    # login FILE
    payload = bytearray()
    payload.extend(map(ord, "FILE"))
    payload.append(0x00)
    result = con._send_recive(command="A_LG", expected_response="T_OK", payload=payload)

    # r_st
    result = con._send_recive(command="R_ST", expected_response="S_ST", payload=None)
    
    # read info 0x05 -> ID
    payload = bytearray()
    payload.append(0x05)
    result = con._send_recive(command="R_VR", expected_response="S_VR", payload=payload)

    # read dir info
    result = con._send_recive(command="R_DI", expected_response="S_DI", payload=None)

    # read dir content 0x01 -> multible entries at a time
    payload = bytearray()
    payload.append(0x01)
    result = con._send_recive_block(command="R_DR", expected_response="S_DR", payload=payload)

    # r_st
    result = con._send_recive(command="R_ST", expected_response="S_ST", payload=None)
    
    time.sleep(3)

    # r_st
    result = con._send_recive(command="R_ST", expected_response="S_ST", payload=None)
    
    time.sleep(3)

    # r_st
    result = con._send_recive(command="R_ST", expected_response="S_ST", payload=None)
    
    # load file
    payload = bytearray()
    payload.extend(map(ord, "TNC:/TOOL_P.TCH"))
    payload.append(0x00)
    response, content = con._llcom.telegram(CMD.R_FL, payload, buffer_size=con._buffer_size)
    
    byte_counter = len(content)
    
    print("response to R_FL was : '{}' content is {} byts long".format(response, byte_counter))
    if response == RSP.S_FL:
        wait_for_more_data = True
        while wait_for_more_data:
            response, content = con._llcom.telegram(RSP.T_OK, payload=None, buffer_size=con._buffer_size)
            if response != RSP.S_FL:
                wait_for_more_data = False
                print("no more data availible or error")
            else:
                byte_counter += len(content)
                print("more data availible")
                time.sleep(1)
    else:
        print("unexpected response")

    print("Bytes recived: {}".format(byte_counter))

    content = con._send_recive(command="R_ST", expected_response="S_ST", payload=None)
    print("response to R_ST was : {}".format(content))

    con.disconnect()
