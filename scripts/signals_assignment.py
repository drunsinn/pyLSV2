# Note: Run this file to dynamically assign the signal numbers to (pyLSV2/pyLSV2/channel_signals.py).

import logging
import pyLSV2
import json
from pathlib import Path
from typing import List

logging.basicConfig(level=logging.INFO)

class SignalConfig():


    def to_json(self, file_path: Path):
        with open(file_path, "w", encoding="utf8") as cfp:
            json.dump(sc.__dict__, cfp)

    @staticmethod
    def from_json(file_path: Path):
        sc = SignalConfig()
        with open(file_path, "r", encoding="utf8") as cfp:
            data = json.load(cfp)

            for key, value in data.items():
                setattr(sc, key, value)
        return sc

    @staticmethod
    def from_signals(signal_list: List[pyLSV2.ScopeSignal]):
        sc = SignalConfig()

        for i, signal in enumerate(signal_list):
            c_name = signal.channel_name.lower()
            c_name = c_name.replace(" ", "_")
            c_name = c_name.replace(".", "_")
            c_name = c_name.replace(":", "_")
            c_name = c_name.replace("(", "_")
            c_name = c_name.replace(")", "")
            c_name = c_name.replace("-", "_")
            c_name = c_name.replace("__", "_")
            c_name = c_name.strip("_")

            s_name = signal.signal_name.lower().strip()

            if len(s_name) > 0:
                full_name = s_name + "_" + c_name
            else:
                full_name = c_name

            setattr(sc, full_name, i)
        
        return sc

with pyLSV2.LSV2("192.168.56.102", port=19000, timeout=5, safe_mode=False) as con:
    availible_signals = con.tst_read_scope_channels()
    # Assigning the signal numbers
    # with open("channel_signals.py",mode="w") as append_channel_signal:
    #     append_channel_signal.write("# Channel Signals:\n")
    #     for i, signal in enumerate(availible_signals):

    #         signal_channel_name = str(signal.channel_name).replace(" ", "_")
    #         signal_channel_name = signal_channel_name.replace(".", "_")
    #         signal_channel_name = signal_channel_name.replace(":", "_")
    #         signal_channel_name = signal_channel_name.replace("(", "_")
    #         signal_channel_name = signal_channel_name.replace(")", "_")
    #         signal_channel_name = signal_channel_name.replace("-", "_")

    #         append_channel_signal.write( "{}_{:s}".format(signal_channel_name, signal.signal_name))
    #         append_channel_signal.write(" = {} ".format(i))
    #         append_channel_signal.write("\n")

    #config_data = dict()
    #config_data["control_verson"] = con.versions.control
    #config_data["software_verson"] = con.versions.nc_sw

    # signal_dict = dict()
    # for i, signal in enumerate(availible_signals):
    #     c_name = signal.channel_name.lower()
    #     c_name = c_name.replace(" ", "_")
    #     c_name = c_name.replace(".", "_")
    #     c_name = c_name.replace(":", "_")
    #     c_name = c_name.replace("(", "_")
    #     c_name = c_name.replace(")", "")
    #     c_name = c_name.replace("-", "_")
    #     c_name = c_name.replace("__", "_")
    #     c_name = c_name.strip("_")

    #     s_name = signal.signal_name.lower().strip()

    #     if len(s_name) > 0:
    #         full_name = s_name + "_" + c_name
    #     else:
    #         full_name = c_name

    #     signal_dict[full_name] = i
    
    # #config_data["signals"] = signal_dict

    # file_name = con.versions.control + "_" +  con.versions.nc_sw + ".json"
    # file_name = file_name.replace(" ", "_")

    # config_file = Path(file_name)
    # with open(config_file, "w", encoding="utf8") as cfp:
    #     json.dump(signal_dict, cfp)


    sc = SignalConfig.from_signals(availible_signals)

    file_name = con.versions.control + "_" +  con.versions.nc_sw + ".json"
    file_name = file_name.replace(" ", "_")
    sc.to_json(Path(file_name))

    print(sc.y_s_actual)

    print(sc.x_i2_t_p_m)
