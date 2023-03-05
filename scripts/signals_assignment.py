{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "INFO:LSV2 Client:disabling safe mode. login and system commands are not restricted. Use with caution!\n",
      "INFO:LSV2 Client:successfully configured connection parameters and basic logins\n",
      "INFO:LSV2 Client:finished loading data\n",
      "INFO:LSV2 Client:logout executed successfully for login None\n"
     ]
    }
   ],
   "source": [
    "#Note: Run this file only once before using the library for the first time. \n",
    "\n",
    "import logging\n",
    "import pyLSV2\n",
    "\n",
    "logging.basicConfig(level=logging.INFO)\n",
    "\n",
    "with pyLSV2.LSV2(\"192.168.56.103\", port=19000, timeout=5, safe_mode=False) as con:\n",
    "    availible_signals = con.tst_read_scope_channels()\n",
    "    # Assigning the signal numbers\n",
    "    with open(\"../pyLSV2/channel_signals.py\",mode=\"w\") as append_channel_signal:\n",
    "        append_channel_signal.write(\"# Channel Signals:\\n\")\n",
    "        for i, signal in enumerate(availible_signals):\n",
    "\n",
    "            signal_channel_name = str(signal.channel_name).replace(\" \", \"_\")\n",
    "            signal_channel_name = signal_channel_name.replace(\".\", \"_\")\n",
    "            signal_channel_name = signal_channel_name.replace(\":\", \"_\")\n",
    "            signal_channel_name = signal_channel_name.replace(\"(\", \"_\")\n",
    "            signal_channel_name = signal_channel_name.replace(\")\", \"_\")\n",
    "            signal_channel_name = signal_channel_name.replace(\"-\", \"_\")\n",
    "\n",
    "            append_channel_signal.write( \"{}_{:s}\".format(signal_channel_name, signal.signal_name))\n",
    "            append_channel_signal.write(\" = {} \".format(i))\n",
    "            append_channel_signal.write(\"\\n\")\n"
   ]
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
  "orig_nbformat": 4
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
