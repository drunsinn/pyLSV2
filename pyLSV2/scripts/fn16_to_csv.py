#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command line script to convert FN16 output files to CSV."""

import argparse
import logging
import sys
from csv import DictWriter
from pathlib import Path
from typing import Dict, List

from pyLSV2.fn16_parser import FN16Parser


def convert_fn16_output_to_csv(format_file: Path, output_file: Path, csv_file: Path) -> None:
    """Convert an FN16 output file into a CSV file using the given format definition."""
    parser = FN16Parser(format_file)
    document = parser.parse_output(output_file)

    rows: List[Dict[str, object]] = []
    header_order: List[str] = []
    seen_variables = set()

    for block in document.blocks:
        row: Dict[str, object] = {}
        for event in block.events:
            if event.type != "data" or not event.values:
                continue
            row.update(event.values)
            for var in event.values:
                if var not in seen_variables:
                    seen_variables.add(var)
                    header_order.append(var)
        if row:
            rows.append(row)

    if not rows:
        raise ValueError(f"No data values found in FN16 output file '{output_file}'")

    csv_file.parent.mkdir(parents=True, exist_ok=True)
    with csv_file.open("w", encoding="utf-8", newline="") as csv_fp:
        writer = DictWriter(csv_fp, fieldnames=header_order, restval="", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an FN16 output file into a CSV file using FN16 format definitions.")
    parser.add_argument("format_file", help="FN16 format definition file", type=Path)
    parser.add_argument("output_file", help="FN16 output file to parse", type=Path)
    parser.add_argument(
        "csv_file",
        help="Target CSV file path. Defaults to output file name with .csv extension.",
        nargs="?",
        type=Path,
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="enable log level DEBUG",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="enable log level INFO",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    if not args.format_file.is_file():
        logging.error("Format file does not exist: %s", args.format_file)
        sys.exit(1)

    if not args.output_file.is_file():
        logging.error("Output file does not exist: %s", args.output_file)
        sys.exit(2)

    csv_file = args.csv_file if args.csv_file is not None else args.output_file.with_suffix(".csv")

    logging.debug("Using format file: %s", args.format_file)
    logging.debug("Parsing output file: %s", args.output_file)
    logging.debug("Writing CSV file: %s", csv_file)

    try:
        convert_fn16_output_to_csv(args.format_file, args.output_file, csv_file)
    except Exception as exc:
        logging.error("Failed to convert FN16 output to CSV: %s", exc)
        sys.exit(3)

    logging.info("CSV export finished: %s", csv_file.absolute())
    sys.exit(0)


if __name__ == "__main__":
    main()
