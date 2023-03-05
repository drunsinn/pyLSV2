#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import pyLSV2
from pyLSV2 import channel_signals

logging.basicConfig(level=logging.INFO)

with pyLSV2.LSV2("192.168.56.103", port=19000, timeout=5, safe_mode=False) as con:
    availible_signals = con.tst_read_scope_channels()

    # build list with selected signals
    selected_signals = list()
    selected_signals.append(availible_signals[channel_signals.s_actual_X])
    selected_signals.append(availible_signals[channel_signals.s_actual_Y])
    selected_signals.append(availible_signals[channel_signals.s_actual_Z])
    selected_signals.append(availible_signals[channel_signals.v_actual_X])
    selected_signals.append(availible_signals[channel_signals.a_actual_X])
    
    print("selected signals:")
    for sig in selected_signals:
        print("# %s" % sig)

    # take readings:
    """
Note: recorded_data[TCP_package_num]["signals"] (that is the yielded value i.e. sample) is a list, its (n)th element is the (n)th appended "availible_signals" in the main code.
    for one_smaple in range(32):
        Signal_type = sample[# appending rank]["data"][one_smaple]
    where:
    Position is /10000    (to be in mm)
    Velocity is *(0.0953652489)   (to be in mm/min)
    Acceleration is *(0.5299145299)    (to be in mm/s^2)
    TODO: Finding the factores of the other channels readings.
"""

    with open("data.txt", "w") as fp:
        for package in con.real_time_readings(
        signal_list=selected_signals, time_readings=10 , intervall_us=3000
    ):
            for one_smaple in range(32): 
                # Signal_type = sample[# appending rank]["data"][one_smaple]
                Position_X = round(package[0]["data"][one_smaple]/10000,3)
                Position_Y = round(package[1]["data"][one_smaple]/10000,3)
                Position_Z = round(package[2]["data"][one_smaple]/10000,3)
                Velocity_X = round(package[3]["data"][one_smaple]*0.0953652489,3)
                Accelera_X = round(package[4]["data"][one_smaple]*0.5299145299,3)

                #print(f"Position X = {Position_X} mm , Position Y = {Position_Y} , Position Z = {Position_Z} , Velocity X = {Velocity_X} mm/min, Acceleration X = {Accelera_X} mm/s^2")
                fp.write(f"Position X = {Position_X} mm , Position Y = {Position_Y} , Position Z = {Position_Z} , Velocity X = {Velocity_X} mm/min, Acceleration X = {Accelera_X} mm/s^2")
                fp.write("\n")
