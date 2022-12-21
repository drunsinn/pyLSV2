#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import time
import pyLSV2
from pyLSV2.const import MemoryType
import struct

logging.basicConfig(level=logging.INFO)

with pyLSV2.LSV2("localhost", port=19000, timeout=5, safe_mode=False) as con:
    print(
            "# Connected to a '{:s}' running software version '{:s}'".format(
                con.versions.control_version, con.versions.nc_version
            )
        )
    
    print("number of scope channels %d" % con.parameters.number_of_scope_channels)
    print("max number of trace lines %d" % con.parameters.max_trace_line)

    channel_list = con.tst_read_scope_channels()

    for channel in channel_list:
        print("Channel No. {:d} of type {:d} : {:s}, interval {:d}us".format(channel.number, channel.type, channel.name, channel.min_interval))
        print(" # signals: {}".format(channel.signals))
        print(" # unknown number: {num1}".format(**channel.unknown))
        print(" # data {dataset}".format(**channel.unknown))


    readings = con.tst_record_data(num_readings=100, intervall_us=6000)

    print(len(readings))
