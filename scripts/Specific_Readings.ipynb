{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "#!/usr/bin/env python3\n",
    "# -*- coding: utf-8 -*-\n",
    "\n",
    "import logging\n",
    "import pyLSV2\n",
    "from pyLSV2 import channel_signals\n",
    "\n",
    "logging.basicConfig(level=logging.INFO)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "INFO:LSV2 Client:disabling safe mode. login and system commands are not restricted. Use with caution!\n",
      "INFO:LSV2 Client:successfully configured connection parameters and basic logins\n",
      "INFO:LSV2 Client:finished loading data\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "selected signals:\n",
      "# Channel/Signal: 02/00 's actual - X' Type 01 Interval 3000us Unit '' Optional Parameter -1\n",
      "# Channel/Signal: 02/01 's actual - Y' Type 01 Interval 3000us Unit '' Optional Parameter -1\n",
      "# Channel/Signal: 02/02 's actual - Z' Type 01 Interval 3000us Unit '' Optional Parameter -1\n",
      "# Channel/Signal: 06/00 'v actual - X' Type 01 Interval 3000us Unit '' Optional Parameter -1\n",
      "# Channel/Signal: 19/00 'a actual - X' Type 01 Interval 3000us Unit '' Optional Parameter -1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "INFO:LSV2 Client:logout executed successfully for login None\n"
     ]
    }
   ],
   "source": [
    "with pyLSV2.LSV2(\"192.168.56.103\", port=19000, timeout=5, safe_mode=False) as con:\n",
    "    availible_signals = con.tst_read_scope_channels()\n",
    "\n",
    "    # build list with selected signals\n",
    "    selected_signals = list()\n",
    "    selected_signals.append(availible_signals[channel_signals.s_actual_X])\n",
    "    selected_signals.append(availible_signals[channel_signals.s_actual_Y])\n",
    "    selected_signals.append(availible_signals[channel_signals.s_actual_Z])\n",
    "    selected_signals.append(availible_signals[channel_signals.v_actual_X])\n",
    "    selected_signals.append(availible_signals[channel_signals.a_actual_X])\n",
    "    \n",
    "    print(\"selected signals:\")\n",
    "    for sig in selected_signals:\n",
    "        print(\"# %s\" % sig)\n",
    "\n",
    "    # take readings:\n",
    "    \"\"\"\n",
    "Note: recorded_data[TCP_package_num][\"signals\"] (that is the yielded value i.e. sample) is a list, its (n)th element is the (n)th appended \"availible_signals\" in the main code.\n",
    "    for one_smaple in range(32):\n",
    "        Signal_type = sample[# appending rank][\"data\"][one_smaple]\n",
    "    where:\n",
    "    Position is /10000    (to be in mm)\n",
    "    Velocity is *(0.0953652489)   (to be in mm/min)\n",
    "    Acceleration is *(0.5299145299)    (to be in mm/s^2)\n",
    "    TODO: Finding the factores of the other channels readings.\n",
    "\"\"\"\n",
    "\n",
    "    with open(\"data.txt\", \"w\") as fp:\n",
    "        for package in con.real_time_readings(\n",
    "        signal_list=selected_signals, time_readings=10 , intervall_us=3000\n",
    "    ):\n",
    "            for one_smaple in range(32): \n",
    "                # Signal_type = sample[# appending rank][\"data\"][one_smaple]\n",
    "                Position_X = round(package[0][\"data\"][one_smaple]/10000,3)\n",
    "                Position_Y = round(package[1][\"data\"][one_smaple]/10000,3)\n",
    "                Position_Z = round(package[2][\"data\"][one_smaple]/10000,3)\n",
    "                Velocity_X = round(package[3][\"data\"][one_smaple]*0.0953652489,3)\n",
    "                Accelera_X = round(package[4][\"data\"][one_smaple]*0.5299145299,3)\n",
    "\n",
    "                #print(f\"Position X = {Position_X} mm , Position Y = {Position_Y} , Position Z = {Position_Z} , Velocity X = {Velocity_X} mm/min, Acceleration X = {Accelera_X} mm/s^2\")\n",
    "                fp.write(f\"Position X = {Position_X} mm , Position Y = {Position_Y} , Position Z = {Position_Z} , Velocity X = {Velocity_X} mm/min, Acceleration X = {Accelera_X} mm/s^2\")\n",
    "                fp.write(\"\\n\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.10.10"
  },
  "orig_nbformat": 4,
  "vscode": {
   "interpreter": {
    "hash": "302f024d7817bdba05a1433852f5d1b1b9f4b97fb0949e00067f8377d0c09cac"
   }
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
