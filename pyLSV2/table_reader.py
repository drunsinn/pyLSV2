#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""module with reader and writer for TNC tables"""
import csv
import json
import logging
import pathlib
import re
from typing import Union


class NCTable:
    """generic object for table files commonly used by TNC, iTNC, CNCPILOT,
    MANUALplus and 6000i CNC
    """

    def __init__(
        self,
        name: str = "",
        suffix: str = "",
        version: str = "",
        has_unit: bool = False,
        is_metric: bool = False,
    ):
        """init object variables logging"""
        self._logger = logging.getLogger("NCTable")
        self.name = name
        self.suffix = suffix
        self.version = version
        self.has_unit = has_unit
        self.is_metric = is_metric
        self._content = []
        self._columns = []
        self._column_format = {}

    def __len__(self):
        """length of table is equal to number of rows in table"""
        return len(self._content)

    @property
    def name(self) -> str:
        """Name of the table read from the header"""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def suffix(self) -> str:
        """file suffix of table"""
        return self._suffix

    @suffix.setter
    def suffix(self, value: str):
        self._suffix = value.lower()

    @property
    def version(self) -> str:
        """version string of from table header"""
        return self._version

    @version.setter
    def version(self, value: str):
        self._version = value

    @property
    def has_unit(self):
        """identifies of values in table are dependent on measuring units"""
        return self._has_unit

    @has_unit.setter
    def has_unit(self, value: bool):
        self._has_unit = value

    @property
    def is_metric(self) -> bool:
        """if true all values should be interpreted as metric"""
        return self._is_metric

    @is_metric.setter
    def is_metric(self, value: bool):
        self._is_metric = value

    @property
    def rows(self) -> list:
        """data entries in this table"""
        return self._content

    @property
    def column_names(self) -> list:
        """list of columns used in this table"""
        return self._columns

    def append_column(self, name: str, start: int, end: int, width: int = 0, empty_value=None):
        """add column to the table format"""
        self._columns.append(name)
        if width == 0:
            width = end - start
        self._column_format[name] = {
            "width": width,
            "start": start,
            "end": end,
            "empty_value": empty_value,
            "min": None,
            "max": None,
            "unique": None,
            "unit": None,
            "read_only": None,
            "is_inch": False,
        }

    def remove_column(self, name: str):
        """remove column by name from table format"""
        self._columns.remove(name)
        del self._column_format[name]

    def get_column_start(self, name: str):
        """get start index of column"""
        return self._column_format[name]["start"]

    def get_column_end(self, name: str):
        """get end index of column"""
        return self._column_format[name]["end"]

    def get_column_width(self, name: str):
        """get width if column"""
        return self._column_format[name]["width"]

    def get_column_empty_value(self, name: str):
        """get value define as default value for column"""
        if "empty_value" in self._column_format[name]:
            return self._column_format[name]["empty_value"]
        return None

    def set_column_empty_value(self, name, value):
        """set the default value of a column"""
        if len(str(value)) > self._column_format[name]["width"]:
            raise ValueError("value to long for column")
        self._column_format[name]["empty_value"] = value

    def update_column_format(self, name: str, parameters: dict):
        """takes a column name and a dictionaly to update the current table configuration"""
        for key, value in parameters.items():
            if key == "unit":
                self._column_format[name]["unit"] = value
            elif key == "minimum":
                self._column_format[name]["min"] = value
            elif key == "maximum":
                self._column_format[name]["max"] = value
            elif key == "unique":
                self._column_format[name]["unique"] = value
            elif key == "initial":
                self._column_format[name]["empty_value"] = value
            elif key == "readonly":
                self._column_format[name]["read_only"] = value
            elif key == "key":
                pass
            elif key == "width":
                pass
            elif key == "unitIsInch":
                self._column_format[name]["is_inch"] = value
            else:
                raise NotImplementedError("key '%s' not implemented" % key)

    def _get_column_names(self):
        """get list of columns used in this table"""
        raise DeprecationWarning("Do not use this function anymore! Use ```column_names```")

    def append_row(self, row):
        """add a data entry to the table"""
        self._content.append(row)

    def extend_rows(self, rows):
        """add multiple data entries at onec"""
        self._content.extend(rows)

    def format_to_json(self) -> str:
        """return json configuration representing the table format"""
        json_data = {}
        json_data["version"] = self.version
        json_data["suffix"] = self.suffix
        json_data["column_list"] = self.column_names
        json_data["column_config"] = self._column_format
        return json.dumps(json_data, ensure_ascii=False, indent=2)

    def dump_native(self, file_path: pathlib.Path, renumber_column=None):
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
                    raise ValueError("configuration is incomplete, missing definition for column {column_name:s}")
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
                                tfp.write(format_string.format(self._column_format[column_name]["empty_value"]))
                            else:
                                raise ValueError("entry is missing a value for column %s defined in the output format" % column_name)
                tfp.write("\n")
                row_counter += 1

            tfp.write("[END]\n")

    def dump_csv(self, file_path: pathlib.Path, decimal_char: str = "."):
        """
        save content of table as csv file

        :param file_path: file location for csv file
        """
        self._logger.debug("write table to csv, using decimal char '%s'", decimal_char)

        def localize_floats(row):
            float_pattern = re.compile(r"^[+-]?\d+\.\d+$")
            for key in row.keys():
                if float_pattern.match(row[key]):
                    row[key] = row[key].replace(".", decimal_char)
            return row

        with open(file_path, "w", newline="", encoding="utf8") as csvfp:
            csv_writer = csv.DictWriter(
                csvfp,
                delimiter=";",
                quotechar='"',
                quoting=csv.QUOTE_ALL,
                fieldnames=self.column_names,
            )
            csv_writer.writeheader()
            for row in self.rows:
                csv_writer.writerow(localize_floats(row))
        self._logger.info("csv file saved successfully")

    def find_string(self, column_name: str, search_value: Union[str, re.Pattern]) -> list:
        """
        search for string rows by string or pattern
        returns list of lines that contain the search result

        :param column_name: name of the table column which should be checked
        :param search_value: the value to check for, can be string or regular expression
        """
        search_results = []
        if not column_name in self._columns:
            self._logger.error("column with name %s not part of this table", column_name)
        else:
            if isinstance(search_value, (str,)):
                search_results = [itm for itm in self._content if search_value in itm[column_name]]
            elif isinstance(search_value, (re.Pattern,)):
                search_results = [itm for itm in self._content if search_value.match(itm[column_name]) is not None]
        return search_results

    @staticmethod
    def parse_table(table_path: pathlib.Path) -> "NCTable":
        """Parse a file of one of the common table formats

        :param str or Path table_path: Path to the table file

        :returns: list of dictionaries. key is the column name, value the content of the table cell
        :rtype: NCTable
        """
        logger = logging.getLogger("NCTable parser")
        nctable = NCTable()

        table_config = None

        table_file = pathlib.Path(table_path)
        if not table_file.is_file():
            raise FileNotFoundError("Could not open file %s" % table_path)

        try:
            with table_file.open(mode="r", encoding="ansi") as tfp:
                header_line = tfp.readline().strip()
                logger.debug("Checking line for header: %s", header_line)
                header = re.match(
                    r"^BEGIN (?P<name>[a-zA-Z_ 0-9]*)\.(?P<suffix>[A-Za-z0-9]{1,4})(?P<unit> MM| INCH)?(?: (Version|VERSION): \'Update:(?P<version>\d+\.\d+)(?: Date:(?P<date>\d{4}-\d{2}-\d{2}))?\')?(?P<mark> U)?$",
                    header_line,
                )

                if header is None:
                    raise ValueError("File has wrong format: incorrect header for file %s" % table_path)

                nctable.name = header.group("name").strip()
                nctable.suffix = header.group("suffix")
                nctable.version = header.group("version")

                if header.group("unit") is not None:
                    nctable.has_unit = True
                    if "MM" in header.group("unit"):
                        nctable.is_metric = True
                        logger.debug(
                            'Header Information for file "%s" Name "%s", file is metric, Version: "%s"',
                            table_file,
                            nctable.name,
                            nctable.version,
                        )
                    else:
                        nctable.is_metric = False
                        logger.debug(
                            'Header Information for file "%s" Name "%s", file is inch, Version: "%s"',
                            table_file,
                            nctable.name,
                            nctable.version,
                        )
                else:
                    nctable.has_unit = False
                    nctable.is_metric = False
                    logger.debug(
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
                    tab_desc = []
                    tab_desc.append(next_line.strip())
                    in_preamble = True
                    next_line = tfp.readline()
                    while in_preamble:
                        tab_desc.append(next_line.strip())
                        if next_line.startswith(")"):
                            in_preamble = False
                        else:
                            next_line = tfp.readline()
                    next_line = tfp.readline()
                    table_config = NCTable.parse_table_description(tab_desc)

                column_pattern = re.compile(r"([A-Za-z-\d_:\.]+)(?:\s+)")
                for column_match in column_pattern.finditer(next_line):
                    if column_match.group().endswith("\n"):
                        cl_end = column_match.end() - 1
                    else:
                        cl_end = column_match.end()
                    nctable.append_column(
                        name=column_match.group().strip(),
                        start=column_match.start(),
                        end=cl_end,
                    )

                logger.debug("Found %d columns", len(nctable.column_names))

                for line in tfp.readlines():
                    if line.startswith("[END]"):
                        break

                    table_entry = {}
                    for column in nctable.column_names:
                        table_entry[column] = line[nctable.get_column_start(column) : nctable.get_column_end(column)].strip()
                    nctable.append_row(table_entry)

                logger.debug("Found %d entries", len(nctable.rows))

                if table_config is not None:
                    logger.debug("update column config from table description")
                    for c_d in table_config["TableDescription"]["columns"]:
                        cfg_column_name = c_d["CfgColumnDescription"]["key"]
                        if cfg_column_name not in nctable.column_names:
                            raise ValueError("found unexpected column %s" % cfg_column_name)
                        if c_d["CfgColumnDescription"]["width"] != nctable.get_column_width(cfg_column_name):
                            raise ValueError(
                                "found difference in column width for colmun %s: %d : %d"
                                % (
                                    cfg_column_name,
                                    c_d["CfgColumnDescription"]["width"],
                                    nctable.get_column_width(cfg_column_name),
                                )
                            )
                        nctable.update_column_format(cfg_column_name, c_d["CfgColumnDescription"])

        except UnicodeDecodeError:
            logger.error("File has invalid utf-8 encoding")
        return nctable

    @staticmethod
    def parse_table_description(lines: list):
        """
        parse the header of a table to get the table configuration

        :param list lines: list of strings cut from the table header
        """
        config_data = {}
        object_list = []
        object_list.append(config_data)

        def str_to_typed_value(value_string: str):
            if re.match(r"^\"?[+-]?\d+[.,]\d+\"?$", value_string):
                return float(value_string.strip('"'))
            if re.match(r"^\"?[+-]?\d+\"?$", value_string):
                return int(value_string.strip('"'))
            if value_string.startswith('"') and value_string.endswith('"'):
                return value_string.strip('"')
            if value_string.upper() == "TRUE":
                return True
            if value_string.upper() == "FALSE":
                return False
            return value_string

        for line in lines:
            line = line.rstrip(",")

            if line.endswith("("):
                last_object = object_list[-1]
                new_category = {}
                name = line.split(" ")[0]
                if isinstance(last_object, (list,)):
                    last_object.append({name: new_category})
                else:
                    if name in last_object:
                        raise ValueError("Element already in dict")
                    last_object[name] = new_category
                object_list.append(new_category)

            elif line.endswith("["):
                last_object = object_list[-1]
                new_group = []
                name = line.split(":=")[0]
                if isinstance(last_object, (list,)):
                    last_object.append({name: new_group})
                else:
                    if name in last_object:
                        raise ValueError("Element already in dict")
                    last_object[name] = new_group
                object_list.append(new_group)

            elif line.endswith(")") or line.endswith("]"):
                object_list.pop()
            else:
                last_object = object_list[-1]
                if isinstance(last_object, (list,)):
                    if ":=" in line:
                        parts = line.split(":=")
                        last_object.append({parts[0]: str_to_typed_value(parts[1])})
                    else:
                        last_object.append(line)

                elif isinstance(last_object, (dict,)):
                    if ":=" in line:
                        parts = line.split(":=")
                        last_object[parts[0]] = str_to_typed_value(parts[1])
                    else:
                        raise ValueError("no keyname??")
                        # last_object["value_%d" % id_counter] = line

        return config_data

    @staticmethod
    def from_json_format(file_path: pathlib.Path) -> "NCTable":
        """return a new NCTable object based on a json configuration file"""
        logger = logging.getLogger("NCTable format parser")
        nct = NCTable()
        with open(file_path, "r", encoding="utf-8") as jfp:
            json_data = json.load(jfp)
            nct.version = json_data["version"]
            nct.suffix = json_data["suffix"]
            for column in json_data["column_config"]:
                logger.debug(
                    "add column %s [%d:%d]",
                    column,
                    json_data["column_config"]["start"],
                    json_data["column_config"][column]["end"],
                )
                nct.append_column(
                    name=column,
                    start=json_data["column_config"][column]["start"],
                    end=json_data["column_config"][column]["end"],
                )
                if "empty_value" in json_data["column_config"][column]:
                    nct.set_column_empty_value(column, json_data["column_config"][column]["empty_value"])
        return nct

    @staticmethod
    def format_entry_float(str_value: str) -> Union[float, None]:
        """convert the string value of a table cell to float value"""
        str_value = str_value.strip()
        if str_value == "-" or len(str_value) == 0:
            return None

        return float(str_value)

    @staticmethod
    def format_entry_int(str_value: str) -> Union[int, None]:
        """convert the string value of a table cell to int value"""
        str_value = str_value.strip()
        if str_value == "-" or len(str_value) == 0:
            return None
        return int(str_value)

    @staticmethod
    def format_entry_bool(str_value: str) -> Union[bool, None]:
        """convert the string value of a table cell to boolean value"""
        str_value = str_value.strip()
        if len(str_value) == 0:
            return None
        if str_value == "1":
            return True
        return False
