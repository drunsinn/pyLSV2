#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import time
import pyLSV2
from pyLSV2.const import MemoryType
import struct

logging.basicConfig(level=logging.DEBUG)

with pyLSV2.LSV2("192.168.56.101", port=19000, timeout=5, safe_mode=False) as con:
    print(
        "# Connected to a '{:s}' running software version '{:s}'".format(
            con.versions.control, con.versions.nc_sw
        )
    )

    print("number of scope channels %d" % con.parameters.number_of_scope_channels)
    print("max number of trace lines %d" % con.parameters.max_trace_line)

    print("encryption key %s" % con.parameters.password_encryption_key)
    exit()


    availible_signals = con.tst_read_scope_channels()

    print("number of available signals: %d" % len(availible_signals))

    # dump available channels to text file
    with open("channels.txt", "w", encoding="utf8") as fp:
        for i, signal in enumerate(availible_signals):
            fp.write("{:03d}: ".format(i))
            fp.write(
                "Channel/Signal: {:02d}/{:02d} Type {:02d} Interval {:d}us".format(
                    signal.channel,
                    signal.signal,
                    signal.channel_type,
                    signal.min_interval,
                )
            )
            fp.write(
                "; channel name: '{:s}' signal name: '{:s}'".format(
                    signal.channel_name, signal.signal_name
                )
            )
            fp.write("\n")

    # build list with selected signals
    selected_signals = list()
    selected_signals.append(availible_signals[0])
    selected_signals.append(availible_signals[1])
    selected_signals.append(availible_signals[2])

    # # select plc channel which needs an additional parameter
    new_sig = availible_signals[133]
    new_sig.signal_parameter = 1000
    selected_signals.append(new_sig)

    # # select plc channel which needs an additional parameter
    new_sig = availible_signals[134]
    new_sig.signal_parameter = 222
    selected_signals.append(new_sig)

    # # select plc channel which needs an additional parameter
    #new_sig = availible_signals[135]
    #new_sig.signal_parameter = 12
    #selected_signals.append(new_sig)

    #selected_signals.append(availible_signals[235])

    print("selected signals:")
    for sig in selected_signals:
        print("# %s" % sig)

    # take readings
    readings = con.tst_record_data(
        signal_list=selected_signals, num_readings=10, intervall_us=21000
    )

    print("number of readins taken: %d" % len(readings))

    # dump data to text file
    with open("data.txt", "w") as fp:
        for entry in readings:
            for num, signal in enumerate(entry["signals"]):
                fp.write("Signal {:02d}:".format(num))
                # fp.write(" header: ")
                # fp.write("".join('{:02x}'.format(x) for x in signal["header"]))
                fp.write(" data: ")
                fp.write(str(signal["data"]))
                fp.write(" ; ")
            fp.write("\n")
