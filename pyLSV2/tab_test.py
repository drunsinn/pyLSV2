#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""module with reader for TNC tables"""
import logging
import re
import json
from pathlib import Path


class ColumnDescription:
    def __init__(self, column_name, format_str):
        self._name = column_name
        self._format = format_str


class TabelFormat:
    def __init__(self):
        self.column_definitions = list()


class GenericTabel:
    @staticmethod
    def from_json(json_path):
        tf = TabelFormat()
        with open(json_path, "r") as jfp:
            data = json.load(jfp)

        for col in data["columns"]:
            print(col)
            cd = ColumnDescription(
                column_name=col["column_name"], format_str=col["format_str"]
            )
            tf.column_definitions.append(cd)


if __name__ == "__main__":
    file = Path("./tool_table.json")
    GenericTabel.from_json(file)
