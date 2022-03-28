#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""module with reader and writer for TNC tables"""
import json
import logging
import re
from pathlib import Path


class TableReader:
    """generic parser for table files commonly used by TNC, iTNC, CNCPILOT,
    MANUALplus and 6000i CNC
    """

    def __init__(self):
        """init object variables logging"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def parse_table(self, table_path):
        """Parse a file of one of the common table formats

        :param str or Path table_path: Path to the table file

        :returns: list od dictionaries. key is the column name, value the content of the table cell
        :rtype: NCTabel
        """
        nctable = NCTabel()

        table_file = Path(table_path)
        if not table_file.is_file():
            raise FileNotFoundError("Could not open file %s" % table_path)

        try:
            with table_file.open(mode="r", encoding="utf-8") as tfp:
                header_line = tfp.readline().strip()
                logging.debug("Checking line for header: %s", header_line)
                header = re.match(
                    r"^BEGIN (?P<name>[a-zA-Z_ 0-9]*)\.(?P<suffix>[A-Za-z0-9]{1,4})(?P<unit> MM| INCH)?(?: (Version|VERSION): \'Update:(?P<version>\d+\.\d+)\')?(?P<mark> U)?$",
                    header_line,
                )

                if header is None:
                    raise Exception(
                        "File has wrong format: incorrect header for file %s"
                        % table_path
                    )

                nctable.name = header.group("name").strip()
                nctable.suffix = header.group("suffix")
                nctable.version = header.group("version")

                if header.group("unit") is not None:
                    nctable.has_unit = True
                    if "MM" in header.group("unit"):
                        nctable.is_metric = True
                        logging.debug(
                            'Header Information for file "%s" Name "%s", file is metric, Version: "%s"',
                            table_file,
                            nctable.name,
                            nctable.version,
                        )
                    else:
                        nctable.is_metric = False
                        logging.debug(
                            'Header Information for file "%s" Name "%s", file is inch, Version: "%s"',
                            table_file,
                            nctable.name,
                            nctable.version,
                        )
                else:
                    nctable.has_unit = False
                    nctable.is_metric = False
                    logging.debug(
                        'Header Information for file "%s" Name "%s", file has no units, Version: "%s"',
                        table_file,
                        nctable.name,
                        nctable.version,
                    )

                next_line = tfp.readline()
                if "#STRUCTBEGIN" in next_line:
                    in_preamble = True
                    next_line = tfp.readline()
                    while in_preamble:
                        if next_line.startswith("#"):
                            in_preamble = False
                        else:
                            next_line = tfp.readline()
                    next_line = tfp.readline()
                elif "TableDescription" in next_line:
                    in_preamble = True
                    next_line = tfp.readline()
                    while in_preamble:
                        if next_line.startswith(")"):
                            in_preamble = False
                        else:
                            next_line = tfp.readline()
                    next_line = tfp.readline()

                column_pattern = re.compile(r"([A-Za-z-12_:\.]+)(?:\s+)")
                for column_match in column_pattern.finditer(next_line):
                    nctable.append_column(
                        name=column_match.group().strip(),
                        start=column_match.start(),
                        end=column_match.end(),
                    )

                logging.debug("Found %d columns", len(nctable.get_column_names()))

                for line in tfp.readlines():
                    if line.startswith("[END]"):
                        break

                    table_entry = {}
                    for column in nctable.get_column_names():
                        table_entry[column] = line[
                            nctable.get_column_start(column) : nctable.get_column_end(
                                column
                            )
                        ].strip()
                    nctable.append_row(table_entry)

                logging.debug("Found %d entries", len(nctable.rows))
        except UnicodeDecodeError:
            logging.error("File has invalid utf-8 encoding")
        return nctable

    @staticmethod
    def format_entry_float(str_value):
        """convert the string value of a table cell to float value"""
        str_value = str_value.strip()
        if str_value == "-" or len(str_value) == 0:
            return None

        return float(str_value)

    @staticmethod
    def format_entry_int(str_value):
        """convert the string value of a table cell to int value"""
        str_value = str_value.strip()
        if str_value == "-" or len(str_value) == 0:
            return None
        return int(str_value)

    @staticmethod
    def format_entry_bool(str_value):
        """convert the string value of a table cell to boolean value"""
        str_value = str_value.strip()
        if len(str_value) == 0:
            return None
        elif str_value == "1":
            return True
        return False


class NCTabel:
    """generic object for table files commonly used by TTNC, iTNC, CNCPILOT,
    MANUALplus and 6000i CNC
    """

    def __init__(
        self, name=None, suffix=None, version=None, has_unit=False, is_metric=False
    ):
        """init object variables logging"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.name = name
        self.suffix = suffix
        self.version = version
        self.has_unit = has_unit
        self.is_metric = is_metric
        self._content = []
        self._columns = []
        self._column_format = {}

    @property
    def name(self):
        """Name of the table read from the header"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def suffix(self):
        """file suffix of table"""
        return self._suffix

    @suffix.setter
    def suffix(self, value):
        if value is None:
            self._suffix = None
        else:
            self._suffix = value.lower()

    @property
    def version(self):
        """version string of from table header"""
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def has_unit(self):
        """identifies of values in table are dependent on measuring units"""
        return self._has_unit

    @has_unit.setter
    def has_unit(self, value):
        self._has_unit = value

    @property
    def is_metric(self):
        """if true all values should be interpreted as metric"""
        return self._is_metric

    @is_metric.setter
    def is_metric(self, value):
        self._is_metric = value

    def append_column(self, name, start, end, width=0, empty_value=None):
        """add column to the table format"""
        self._columns.append(name)
        if width == 0:
            width = end - start
        self._column_format[name] = {
            "width": int(width),
            "start": int(start),
            "end": int(end),
        }
        if empty_value is not None:
            self._column_format[name]["empty_value"] = empty_value

    def remove_column(self, name):
        """remove column by name from table format"""
        self._columns.remove(name)
        del self._column_format[name]

    def get_column_start(self, name):
        """get start index of column"""
        return self._column_format[name]["start"]

    def get_column_end(self, name):
        """get end index of column"""
        return self._column_format[name]["end"]

    def get_column_width(self, name):
        """get width if column"""
        return self._column_format[name]["width"]

    def get_column_empty_value(self, name):
        """get value define as default value for column"""
        if "empty_value" in self._column_format[name]:
            return self._column_format[name]["empty_value"]
        else:
            return None

    def set_column_empty_value(self, name, value):
        """set the default value of a column"""
        if len(str(value)) > self._column_format[name]["width"]:
            raise Exception("value to long for column")
        self._column_format[name]["empty_value"] = value

    def get_column_names(self):
        """get list of columns used in this table"""
        return self._columns

    def append_row(self, row):
        """add a data entry to the table"""
        self._content.append(row)

    def extend_rows(self, rows):
        """add multiple data entries at onec"""
        self._content.extend(rows)

    @property
    def rows(self):
        """data entries in this table"""
        return self._content

    def format_to_json(self):
        """return json configuration representing the table format"""
        json_data = {}
        json_data["version"] = self.version
        json_data["suffix"] = self.suffix
        json_data["column_list"] = self.get_column_names()
        json_data["column_config"] = self._column_format
        return json.dumps(json_data, ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(file_path):
        """return a new NCTable object based on a json configuration file"""
        with open(file_path, "r", encoding="utf-8") as jfp:
            json_data = json.load(jfp)
            nct = NCTabel()
            nct.version = json_data["version"]
            nct.suffix = json_data["suffix"]
            for column in json_data["column_config"]:
                nct.append_column(
                    name=column,
                    start=json_data["column_config"][column]["start"],
                    end=json_data["column_config"][column]["end"],
                )
                if "empty_value" in json_data["column_config"][column]:
                    nct.set_column_empty_value(
                        column, json_data["column_config"][column]["empty_value"]
                    )
        return nct

    def dump(self, file_path, renumber_column=None):
        """write table data to a file in the format used by the controls"""
        row_counter = 0
        file_name = file_path.name.upper()

        units_string = ""
        if self._has_unit:
            if self._is_metric:
                units_string = " MM"
            else:
                units_string = " INCH"
        version_string = ""
        if self._version is not None:
            version_string = " Version:%s" % str(self._version)

        with open(file_path, "w", encoding="ascii") as tfp:
            tfp.write("BEGIN %s%s%s\n" % (file_name, units_string, version_string))

            for column_name in self._columns:
                if column_name not in self._column_format:
                    raise Exception(
                        "configuration is incomplete, missing definition for column {column_name:s}"
                    )
                fixed_width = self._column_format[column_name]["width"]
                format_string = "{0:<%d}" % fixed_width
                tfp.write(format_string.format(column_name))
            tfp.write("\n")

            for row in self._content:
                for column_name in self._columns:
                    fixed_width = self._column_format[column_name]["width"]
                    format_string = "{0:<%d}" % fixed_width

                    if column_name is renumber_column:
                        tfp.write(format_string.format(row_counter))
                    else:
                        if column_name in row:
                            tfp.write(format_string.format(row[column_name]))
                        else:
                            if "empty_value" in self._column_format[column_name]:
                                logging.warning(
                                    "entry is missing optional column %s defined in output format, replace with empty value",
                                    column_name,
                                )
                                tfp.write(
                                    format_string.format(
                                        self._column_format[column_name]["empty_value"]
                                    )
                                )
                            else:
                                raise Exception(
                                    "entry is missing a value for column %s defined in the output format"
                                    % column_name
                                )
                tfp.write("\n")
                row_counter += 1

            tfp.write("[END]\n")
