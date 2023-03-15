#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import argparse
from pathlib import Path
from typing import List

import pyLSV2

logging.basicConfig(level=logging.INFO)


class SignalConfig:
    def to_json(self, file_path: Path):
        with open(file_path, "w", encoding="utf8") as cfp:
            json.dump(sc.__dict__, cfp)

    @staticmethod
    def from_json(file_path: Path):
        signal_config = SignalConfig()
        with open(file_path, "r", encoding="utf8") as cfp:
            data = json.load(cfp)

            for key, value in data.items():
                setattr(signal_config, key, value)
        return signal_config

    @staticmethod
    def from_signals(signal_list: List[pyLSV2.ScopeSignal]):
        signal_config = SignalConfig()

        for i, signal in enumerate(signal_list):
            setattr(signal_config, signal.normalized_name(), i)

        return signal_config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="command line script for dumping the signal list of a control to json"
    )
    parser.add_argument(
        "address",
        help="ip or hostname of the control",
        type=str,
    )
    parser.add_argument(
        "destination",
        help="destination json file",
        type=Path,
    )

    args = parser.parse_args()

    with pyLSV2.LSV2(args.address, port=19000, timeout=5, safe_mode=False) as con:
        availible_signals = con.read_scope_signals()

        # create signal configuration from signal list
        sc = SignalConfig.from_signals(availible_signals)

        # store signal configuration to json file
        sc.to_json(args.destination)

        # restore signal configuration from json file
        sc_new = SignalConfig.from_json(args.destination)

        # compare before and after
        print(sc.y_s_actual, sc_new.y_s_actual)

        print(sc.x_i2_t_p_m, sc_new.x_i2_t_p_m)
