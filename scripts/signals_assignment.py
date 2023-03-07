# Note: Run this file to dynamically assign the signal numbers to (pyLSV2/pyLSV2/channel_signals.py).

import logging
import pyLSV2

logging.basicConfig(level=logging.INFO)

with pyLSV2.LSV2("192.168.56.103", port=19000, timeout=5, safe_mode=False) as con:
    availible_signals = con.tst_read_scope_channels()
    # Assigning the signal numbers
    with open("../pyLSV2/channel_signals.py",mode="w") as append_channel_signal:
        append_channel_signal.write("# Channel Signals:\n")
        for i, signal in enumerate(availible_signals):

            signal_channel_name = str(signal.channel_name).replace(" ", "_")
            signal_channel_name = signal_channel_name.replace(".", "_")
            signal_channel_name = signal_channel_name.replace(":", "_")
            signal_channel_name = signal_channel_name.replace("(", "_")
            signal_channel_name = signal_channel_name.replace(")", "_")
            signal_channel_name = signal_channel_name.replace("-", "_")

            append_channel_signal.write( "{}_{:s}".format(signal_channel_name, signal.signal_name))
            append_channel_signal.write(" = {} ".format(i))
            append_channel_signal.write("\n")
