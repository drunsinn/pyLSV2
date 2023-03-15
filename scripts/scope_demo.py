#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script contains a demo on how to use the scope functions on iTNC controls
"""

import sys
import logging
import pyLSV2

logging.basicConfig(level=logging.WARNING)

with pyLSV2.LSV2("192.168.56.102", port=19000, timeout=5, safe_mode=False) as con:
    if not con.versions.is_itnc():
        print("the scope functions only work for iTNC controls")
        sys.exit(-1)

    availible_signals = con.read_scope_signals()

    # build list with selected signals
    selected_signals = list()
    selected_signals.append(availible_signals[0])
    selected_signals.append(availible_signals[1])
    selected_signals.append(availible_signals[2])

    print("selected signals:")
    for sig in selected_signals:
        print("# %s" % sig)

    duration = 2
    interval = 6000

    print("reading values for a duration of %d seconds with an interval of %d µs")

    # take readings:
    readings_counter = 0

    for package in con.real_time_readings(selected_signals, duration, interval):
        signal_readings = package.get_data()
        readings_per_signal = len(signal_readings[0].data)
        print(
            "successfully read %d signals with %d values each"
            % (len(signal_readings), readings_per_signal)
        )

        for i in range(readings_per_signal):
            position_X = (
                signal_readings[0].data[i] * signal_readings[0].factor
                + signal_readings[0].offset
            )
            position_Y = (
                signal_readings[1].data[i] * signal_readings[1].factor
                + signal_readings[1].offset
            )
            position_Z = (
                signal_readings[2].data[i] * signal_readings[2].factor
                + signal_readings[2].offset
            )
            readings_counter += 1

            print(
                "Count: %d Position X = %.3f mm, Position Y = %.3f, Position Z = %.3f"
                % (readings_counter, position_X, position_Y, position_Z)
            )

    print("# a total of %d readings were taken" % readings_counter)

    print("# the signal description was updated to:")
    for signal in selected_signals:
        print("##", signal)
