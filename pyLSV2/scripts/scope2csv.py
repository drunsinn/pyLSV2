#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""With this script you can read scope values from a iTNC control and save the data as a csv file
"""
import sys
import logging
import argparse
from csv import writer as csv_writer
from pathlib import Path

import pyLSV2


__author__ = "Md-aliy7 & drunsinn"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "dr.unsinn@googlemail.com"


def main():
    parser = argparse.ArgumentParser(
        prog="real_time_readings",
        description="script to read scope signals from control",
        epilog="for more information on pyLSV2, visit https://github.com/drunsinn/pyLSV2",
    )

    parser.add_argument("host", help="ip or hostname of control", type=str)

    parser.add_argument("output", help="path of the csv file the data should be written to", type=Path)

    parser.add_argument(
        "signals",
        help="list of signal numbers to record. separated by spaces",
        nargs="+",
        type=int,
    )

    parser.add_argument("-a", "--duration", help="number of seconds to record", type=int, default=10)

    parser.add_argument(
        "-i",
        "--interval",
        help="number of µs between readings",
        type=int,
        default=21000,
    )

    parser.add_argument(
        "-d",
        "--debug",
        help="Print logging messages including debug statements",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print logging messages including info statements",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    parser.add_argument(
        "-t",
        "--time_out",
        help="number of seconds to wait for connection, default is 5",
        dest="timeout",
        type=int,
        default=5,
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    logging.debug(
        "Command line arguments: Host: '%s', Timeout %d, Destination '%s'",
        args.host,
        args.timeout,
        args.output,
    )
    logging.debug(
        "Command line arguments: Duration: %d, Signals %s, Interval %d",
        args.duration,
        args.signals,
        args.interval,
    )

    selected_signals = args.signals
    if sorted(selected_signals)[0] < 0:
        logging.error(
            "the selected signal numbers contain at least one negative value: %d",
            selected_signals[0],
        )
        sys.exit(-1)

    if args.duration <= 0:
        logging.error(
            "the selected recording duration has to be greater than 0: %d",
            args.duration,
        )
        sys.exit(-2)

    if args.interval <= 0:
        logging.error("the selected interval has to be at least greater than 0: %d", args.interval)
        sys.exit(-3)

    with pyLSV2.LSV2(args.host, port=19000, timeout=args.timeout, safe_mode=False) as con:
        availible_signals = con.read_scope_signals()

        if sorted(selected_signals)[-1] > len(availible_signals):
            logging.error(
                "the selected signal number is outside the rage of available signals of %s",
                len(availible_signals),
            )
            sys.exit(-10)

        scope_signals = list()
        for signal in selected_signals:
            new_signal = availible_signals[signal]
            logging.info(
                "selecting signal %d, '%s' witch has a minimal interval of %dµs",
                signal,
                new_signal.normalized_name(),
                new_signal.min_interval,
            )
            scope_signals.append(new_signal)

        with open(args.output, "w", encoding="utf8") as csv_fp:
            csv = csv_writer(csv_fp, dialect="excel", lineterminator="\n")
            csv.writerow(list(map(lambda x: x.normalized_name(), scope_signals)))
            readings_counter = 0

            for package in con.real_time_readings(scope_signals, args.duration, args.interval):
                signal_readings = package.get_data()
                readings_per_signal = len(signal_readings[0].data)
                logging.debug(
                    "successfulle read %d signals with %d values each",
                    len(signal_readings),
                    readings_per_signal,
                )

                for i in range(readings_per_signal):
                    row = []
                    for signal in signal_readings:
                        value = (signal.data[i] * signal.factor) + signal.offset
                        row.append(value)
                    csv.writerow(row)
                    readings_counter += 1

        logging.info("finished reading data, data was saved to %s", args.output.absolute())
        logging.debug("number of recorded data points %d", readings_counter)

        for s in scope_signals:
            logging.info(
                "updated information for signal '%s': unit '%s'",
                s.normalized_name(),
                s.unit,
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
