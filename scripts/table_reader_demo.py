#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import pathlib
from pyLSV2 import TableReader, NCTabel

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    tr = TableReader()

    input_file = pathlib.Path("../data/tool.t")

    # read table
    nc_table = tr.parse_table(input_file)

    # safe table format to json
    if nc_table.version is not None:
        format_file_name = "output_format_%s.json" % str(nc_table.version)
    else:
        format_file_name = "output_format_generic.json"
    format_file_path = input_file.parents[0] / format_file_name
    with open(format_file_path, "w", encoding="utf-8") as fp:
        fp.write(nc_table.format_to_json())

    # combine two tables
    second_file = pathlib.Path("../data/tool2.t")
    output_table = input_file.parents[0] / "combined.t"
    second_table = tr.parse_table(second_file)
    nc_table.extend_rows(second_table.rows)
    nc_table.dump(output_table, renumber_column="T")
