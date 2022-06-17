#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import sys

import time
import pyLSV2
from pyLSV2.const import CMD, RSP, ParCCC

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    address = "localhost"
    if len(sys.argv) > 1:
        address = sys.argv[1]

    print("Connecting to {}".format(address))

    logging.basicConfig(level=logging.DEBUG)
    con = pyLSV2.LSV2("localhost", port=19000, timeout=5, safe_mode=False)

    con.connect()

    # force lower buffer size
    con.set_system_command(ParCCC.SET_BUF2048)
    con._buffer_size = 2048
    print("Connection uses buffer size {}".format(con._buffer_size))

    s_st_content = con._send_recive(command="R_ST", expected_response="S_ST", payload=None)
    print("response to R_ST was : {}".format(s_st_content))

    con.change_directory("TNC:/")

    payload = bytearray()
    payload.extend(map(ord, "TNC:/TOOL_P.TCH"))
    payload.append(0x00)

    response, content = con._llcom.telegram(CMD.R_FL, payload, buffer_size=con._buffer_size)
    
    byte_counter = len(content)

    time.sleep(1)
    
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

    if s_st_content is content:
        print("both S_ST respones match")
    else:
        print("both S_ST respones do not match")

    con.disconnect()
