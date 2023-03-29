#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import pyLSV2

logging.basicConfig(level=logging.WARNING)

with pyLSV2.LSV2("192.168.56.102", port=19000, timeout=5, safe_mode=False) as con:
    availible_signals = con.read_scope_signals()

    # build list with selected signals
    selected_signals = list()
    selected_signals.append(availible_signals[0])
    selected_signals.append(availible_signals[1])
    selected_signals.append(availible_signals[2])
    # alternatively: find signal by normalized name
    # selected_signals.append(next(signal for signal in availible_signals if signal.normalized_name() == "x_s_actual"))
    # selected_signals.append(next(signal for signal in availible_signals if signal.normalized_name() == "y_s_actual"))
    # selected_signals.append(next(signal for signal in availible_signals if signal.normalized_name() == "z_s_actual"))
    # selected_signals.append(next(signal for signal in availible_signals if signal.normalized_name() == "x_v_actual"))
    # selected_signals.append(next(signal for signal in availible_signals if signal.normalized_name() == "x_a_actual"))

    duration = 10
    interval = 3000

    print("selected signals:")
    for sig in selected_signals:
        print("# %s" % sig)

    # take readings:
    # signal_list=selected_signals, duration=10 , interval=3000):
    with open("data.txt", "w") as fp:
        readings_counter = 0

        for package in con.real_time_readings(selected_signals, duration, interval):
            signal_readings = package.get_data()
            readings_per_signal = len(signal_readings[0].data)
            print(
                "successfulle read %d signals with %d values each"
                % (len(signal_readings), readings_per_signal)
            )

            for i in range(readings_per_signal):
                # Signal_type = sample[# appending rank]["data"][one_smaple]
                # for signal in signal_readings:
                #    value = (signal.data[i] * signal.factor) + signal.offset
                #    print(value, signal.unit)

                position_X = round(
                    signal_readings[0].data[i] * signal_readings[0].factor
                    + signal_readings[0].offset,
                    3,
                )
                position_Y = round(
                    signal_readings[1].data[i] * signal_readings[1].factor
                    + signal_readings[1].offset,
                    3,
                )
                position_Z = round(
                    signal_readings[2].data[i] * signal_readings[2].factor
                    + signal_readings[2].offset,
                    3,
                )
                # velocity_X = round(signal_readings[3].data[i]*0.0953652489,3)
                # acceleration_X = round(signal_readings[4].data[i]*0.5299145299,3)

                # print(f"Position X = {Position_X} mm , Position Y = {Position_Y} , Position Z = {Position_Z} , Velocity X = {Velocity_X} mm/min, Acceleration X = {Accelera_X} mm/s^2")
                fp.write(
                    "Position X = %f mm , Position Y = %f , Position Z = %f\n"
                    % (position_X, position_Y, position_Z)
                )
            readings_counter += 1

    print("a total of %d readings were taken" % readings_counter)

    print("the signal description was updated to:")
    for s in selected_signals:
        print(s)
