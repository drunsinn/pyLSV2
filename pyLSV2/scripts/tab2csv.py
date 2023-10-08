#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""script to convert table files to csv"""
import argparse
import logging
import pathlib
import sys

from pyLSV2 import NCTable


def main():
    """console application to convert a tnc table file to a csv file"""
    parser = argparse.ArgumentParser(description="command line script parsing table files")
    parser.add_argument("source", help="table file to parse", type=pathlib.Path)
    parser.add_argument("--decimal_char", help="override local decimal char", type=str, default=",")
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "-d",
        "--debug",
        help="enable log level DEBUG",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    log_group.add_argument(
        "-v",
        "--verbose",
        help="enable log level INFO",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    logging.debug('Start logging with level "%s"', logging.getLevelName(args.loglevel))

    if args.source.is_file():
        nc_table = NCTable.parse_table(args.source)
        print("number of rows in table: %d" % len(nc_table))
        print("columns in table %s" % nc_table.column_names)
        if nc_table.has_unit:
            print("table file specifies unit system")
            if nc_table.is_metric:
                print("values are metric")
            else:
                print("values are imperial")
        else:
            print("table has no apparent unit system")

        csv_file_name = args.source.with_suffix(".csv")
        print("write table to file %s" % csv_file_name)
        nc_table.dump_csv(csv_file_name, args.decimal_char)
        print("csv export finished")

    else:
        print("table file does not exits %s" % args.source)
        sys.exit(-1)

    sys.exit(0)


if __name__ == "__main__":
    main()
