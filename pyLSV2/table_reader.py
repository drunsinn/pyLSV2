#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reader and writer for CNC table files in fixed-width format.

This module handles parsing and serializing table files commonly used by Heidenhain CNC controllers
(TNC, iTNC, CNCPILOT, MANUALplus, 6000i) and other manufacturers. It supports three distinct
table format types differentiated by their header structure:

- Type 1: No header description (simple fixed-width columns)
- Type 2: Old-style #STRUCTBEGIN/#STRUCTEND structured headers
- Type 3: New-style TableDescription structured headers

Each format type carries optional metadata about columns (units, min/max values, etc.)
that can be extracted and applied to table configurations.
"""

import csv
import json
import logging
import pathlib
import re
from typing import Union, List, Dict, Any

# Header parsing patterns
_HEADER_PATTERN = re.compile(
    r"BEGIN (?P<name>[a-zA-Z_ 0-9-]*(?= MM|INCH|\.))(?P<suffix>\.[A-Za-z0-9\.]*)?(?P<unit> MM| INCH)?"
    r"(?: (Version|VERSION): \'Update:(?P<version>\d+\.\d+)(?: Date:(?P<date>\d{4}-\d{2}-\d{2}))?\')?"
    r"(?: (?P<mark>U))?"
)


class NCTable:
    """Container for CNC table data with configurable fixed-width columns.

    Represents a parsed or constructed table file with metadata about columns (name, position,
    width, units, constraints) and row data. Supports reading from and writing to CNC-native,
    CSV, and JSON formats.

    :param str name: Table identifier from file header
    :param str suffix: File extension/suffix (e.g., 't', 'tab', 'cdt')
    :param str version: Version string from header (if present)
    :param bool has_unit: True if table values have unit constraints (MM/INCH)
    :param bool is_metric: True if unit is MM; False if INCH or unitless
    """

    def __init__(
        self,
        name: str = "",
        suffix: str = "",
        version: str = "",
        has_unit: bool = False,
        is_metric: bool = False,
    ):
        """Initialize a new NCTable object.

        Args:
            name: Table identifier from file header
            suffix: File extension or format suffix
            version: Version string from file header
            has_unit: Whether table values have unit constraints
            is_metric: Unit system (True=MM, False=INCH or unitless)
        """
        self._logger = logging.getLogger("NCTable")
        self.name = name
        self.suffix = suffix
        self.version = version
        self.has_unit = has_unit
        self.is_metric = is_metric
        self._content: List[Dict[str, str]] = []
        self._columns: List[str] = []
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
        if self._suffix is not None:
            return self._suffix.lower()
        return ""

    @suffix.setter
    def suffix(self, value: str):
        if value is not None:
            self._suffix = value.lower()
        else:
            self._suffix = None

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
    def rows(self) -> List[Dict[str, str]]:
        """data entries in this table"""
        return self._content

    @property
    def column_names(self) -> List[str]:
        """list of columns used in this table"""
        return self._columns

    def append_column(self, name: str, start: int, end: int, width: int = 0, empty_value: Any = None):
        """Register a column in this table's schema.

        :param str name: Column identifier
        :param int start: Starting byte offset in fixed-width rows
        :param int end: Ending byte offset (exclusive), or -1 for open-ended final column
        :param int width: Column width in bytes. Computed as (end - start) if 0
        :param Any empty_value: Default value for missing data in this column
        """
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
        """Unregister a column from this table's schema.

        :param str name: Column identifier to remove
        
        :raises: ValueError if column is not present
        """
        self._columns.remove(name)
        del self._column_format[name]

    def get_column_start(self, name: str) -> int:
        """Get the starting byte offset of a column.

        :param str name: Column identifier
        
        :returns: Starting byte offset in fixed-width rows
        """
        return self._column_format[name]["start"]

    def get_column_end(self, name: str) -> int:
        """Get the ending byte offset of a column.

        :param str name: Column identifier
        
        :return: Ending byte offset (exclusive), or -1 for open-ended final column
        :rtype: int
        """
        return self._column_format[name]["end"]

    def get_column_width(self, name: str) -> int:
        """Get the width of a column in bytes.

        :param str name: Column identifier
        :return: Column width in bytes
        :rtype: int
        """
        return self._column_format[name]["width"]

    def get_column_empty_value(self, name: str) -> Any:
        """Get the default value for a column.

        :param str name: Column identifier
        
        :return: Default value or None if not configured
        :rtype: Any
        """
        if "empty_value" in self._column_format[name]:
            return self._column_format[name]["empty_value"]
        return None

    def set_column_empty_value(self, name: str, value: Any):
        """Set the default value for a column.

        :param str name: Column identifier
        :param Any value: Default value to use when column data is missing
        
        :raises: ValueError if value is wider than the column
        """
        if len(str(value)) > self._column_format[name]["width"]:
            raise ValueError("value to long for column")
        self._column_format[name]["empty_value"] = value

    def update_column_format(self, name: str, parameters: Dict):
        """Apply metadata constraints to a column's configuration.

        Supported metadata keys:
        - unit: Data type (INT, FLOAT, TEXT)
        - minimum: Minimum allowed value
        - maximum: Maximum allowed value
        - unique: Whether values must be unique in this column
        - initial: Default value when creating new rows
        - readonly: Whether column is read-only
        - decimals: Number of decimal places (stored but not interpreted)
        - unitIsInch: Whether unit values are in inches vs metric

        :param str name: Column identifier
        :param Dict parameters: Dict of metadata key-value pairs to apply
        
        :raises: NotImplementedError: If a parameter key is not recognized
        """
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
                pass  # dont update key
            elif key == "width":
                self._column_format[name]["width"] = value
                if self._column_format[name]["end"] != -1:
                    self._column_format[name]["end"] = self._column_format[name]["start"] + value
            elif key == "decimals":
                pass  # TODO work out how to store number of decimal places
            elif key == "unitIsInch":
                self._column_format[name]["is_inch"] = value
            else:
                raise NotImplementedError("key '%s' not implemented" % key)

    def _get_column_names(self):
        """get list of columns used in this table"""
        raise DeprecationWarning("Do not use this function anymore! Use ```column_names```")

    def append_row(self, row: Dict[str, str]):
        """Add a data row to this table.

        :param Dict[str, str] row: Dict mapping column names to their values (as strings)
        """
        self._content.append(row)

    def extend_rows(self, rows: List[Dict[str, str]]):
        """Add multiple data rows to this table.

        :param List[Dict[str, str]] rows: List of dicts, each mapping column names to their values
        """
        self._content.extend(rows)

    def format_to_json(self) -> str:
        """return json configuration representing the table format
        
        :returns: JSON string with table format information (version, suffix, column list, column config)
        :rtype: str
        """
        json_data = {}
        json_data["version"] = self.version
        json_data["suffix"] = self.suffix
        json_data["column_list"] = self.column_names
        json_data["column_config"] = self._column_format
        return json.dumps(json_data, ensure_ascii=False, indent=2)

    def dump_native(self, file_path: pathlib.Path, renumber_column: Union[str, None] = None):
        """Write table data to a CNC-native format file.

        :param pathlib.Path file_path: Output file path
        :param Union[str, None] renumber_column: If specified, renumber this column sequentially (0, 1, 2, ...)
        """
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
        """Write table data to a CSV file with localized decimal separator.

        :param pathlib.Path file_path: Output CSV file path
        :param str decimal_char: Character to use as decimal separator (e.g., ',' for European format)
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
        """Find rows where a column matches a value or pattern.

        :param str column_name: Column identifier to search in
        :param Union[str, re.Pattern] search_value: String (substring match) or compiled regex Pattern
        
        :returns: List of row dicts that match the search criterion
        """
        search_results = []
        if column_name not in self._columns:
            self._logger.error("column with name %s not part of this table", column_name)
        else:
            if isinstance(search_value, (str,)):
                search_results = [itm for itm in self._content if search_value in itm[column_name]]
            else:
                search_results = [itm for itm in self._content if search_value.match(itm[column_name]) is not None]
        return search_results

    @staticmethod
    def parse_header(header_line: str) -> Dict[str, Any]:
        """Parse the first line of a table file to extract metadata.

        Expected format: BEGIN <name> [.<suffix>] [MM|INCH] [Version: 'Update:X.Y[ Date:YYYY-MM-DD]'] [U]

        :param str header_line: First line of the table file (with leading/trailing whitespace stripped)
        
        :returns: Dict with keys: name, suffix, version, date, mark, unit
        :rtype: Dict[str, Any]

        :raises ValueError: If header format is invalid or unrecognized
        """
        header_data: Dict[str, Any] = {}
        logger = logging.getLogger("NCTable header parser")
        header_line = header_line.strip()
        logger.debug("Checking line for header: %s", header_line)
        result = _HEADER_PATTERN.fullmatch(header_line)

        if result is None:
            raise ValueError("File has wrong format: incorrect header: %s" % header_line)

        header_data["name"] = result.group("name").strip()
        header_data["suffix"] = None
        if result.group("suffix") is not None:
            header_data["suffix"] = result.group("suffix").lstrip(".")
        header_data["version"] = result.group("version")
        header_data["date"] = result.group("date")
        header_data["mark"] = result.group("mark")
        header_data["unit"] = ""

        if result.group("unit") is not None:
            if "MM" in result.group("unit"):
                header_data["unit"] = "MM"
            else:
                header_data["unit"] = "INCH"

        logger.debug("Header Information for table '%s'", header_data["name"])

        return header_data

    @staticmethod
    def _read_nested_description(start_line: str, stream) -> List[str]:
        """Read a structured description block with balanced nesting.

        Reads lines from stream until top-level parentheses/brackets are balanced,
        respecting string literals and escape sequences. Used for TableDescription
        and similar structured header blocks.

        :param str start_line: First line of the block (may be incomplete)
        :param TextIO stream: Open file object positioned after start_line

        :returns: List of stripped lines comprising the complete nested block
        :rtype: List[str]

        :raises ValueError: If EOF reached before nesting is balanced
        """
        lines = [start_line.strip()]
        nesting = 0
        in_quote = False
        escaped = False

        def process_char(character: str) -> None:
            nonlocal nesting, in_quote, escaped
            if escaped:
                escaped = False
                return
            if character == "\\":
                escaped = True
                return
            if character == '"':
                in_quote = not in_quote
                return
            if in_quote:
                return
            if character in ('(', '['):
                nesting += 1
            elif character in (')', ']'):
                nesting -= 1

        for char in start_line:
            process_char(char)

        while nesting > 0:
            line = stream.readline()
            if line == "":
                raise ValueError("Unexpected end of file while reading structured header")
            stripped = line.strip()
            lines.append(stripped)
            for char in line:
                process_char(char)

        return lines

    @staticmethod
    def parse_table(table_path: pathlib.Path) -> "NCTable":
        """Parse a file of one of the common table formats.

        :param table_path: path to a table file (Path-like object)
        :type table_path: pathlib.Path

        :returns: NCTable object containing parsed rows and columns
        :rtype: NCTable
        """
        logger = logging.getLogger("NCTable parser")
        nctable = NCTable()

        table_config = None

        table_file = pathlib.Path(table_path)
        if not table_file.is_file():
            raise FileNotFoundError("Could not open file %s" % table_path)

        try:
            with table_file.open(mode="r", encoding="latin1") as tfp:
                header_data = NCTable.parse_header(tfp.readline())
                nctable.name = header_data["name"]
                nctable.suffix = header_data["suffix"]
                nctable.version = header_data["version"]
                if len(header_data["unit"]) < 1:
                    nctable.has_unit = False
                else:
                    nctable.has_unit = True
                    nctable.is_metric = header_data["unit"] == "MM"

                next_line = tfp.readline()
                while next_line and next_line.strip() == "":
                    next_line = tfp.readline()

                if next_line is None or next_line == "":
                    raise ValueError("Missing column header after table description")

                if "#STRUCTBEGIN" in next_line:
                    tab_desc = [next_line.strip()]
                    while True:
                        next_line = tfp.readline()
                        if next_line == "":
                            raise ValueError("Unexpected end of file while reading #STRUCTBEGIN block")
                        stripped = next_line.strip()
                        tab_desc.append(stripped)
                        if stripped.startswith("#STRUCTEND"):
                            break
                    next_line = tfp.readline()
                    table_config = NCTable.parse_table_structure(tab_desc)

                elif "TableDescription" in next_line:
                    tab_desc = NCTable._read_nested_description(next_line, tfp)
                    next_line = tfp.readline()
                    table_config = NCTable.parse_table_description(tab_desc)

                while next_line and next_line.strip() == "":
                    next_line = tfp.readline()

                if next_line is None or next_line == "":
                    raise ValueError("Missing column header line after table description")

                column_pattern = re.compile(r"([A-Za-z-\d_:\.]+)(?:\s+|$)")
                header_line = next_line.rstrip("\n")
                matches = list(column_pattern.finditer(next_line))
                for index, column_match in enumerate(matches):
                    if index == len(matches) - 1 or header_line[column_match.end():].strip() == "":
                        cl_end = -1
                        width = len(header_line) - column_match.start()
                    else:
                        cl_end = column_match.end()
                        width = cl_end - column_match.start()

                    nctable.append_column(
                        name=column_match.group().strip(),
                        start=column_match.start(),
                        end=cl_end,
                        width=width,
                    )

                logger.debug("Found %d columns", len(nctable.column_names))

                for line in tfp:
                    if not line.strip():
                        continue
                    if line.strip().startswith("[END]") or line.strip().upper() == "END":
                        break

                    table_entry = {}
                    for column in nctable.column_names:
                        column_start = nctable.get_column_start(column)
                        column_end = nctable.get_column_end(column)
                        if column_end == -1:
                            table_entry[column] = line[column_start:].strip()
                        else:
                            table_entry[column] = line[column_start:column_end].strip()
                    nctable.append_row(table_entry)

                logger.debug("Found %d entries", len(nctable.rows))

                if table_config is not None:
                    logger.debug("update column config from table description")
                    for c_d in table_config["TableDescription"]["columns"]:
                        cfg_column_name = c_d["CfgColumnDescription"]["key"]
                        if cfg_column_name not in nctable.column_names:
                            raise ValueError("found unexpected column %s" % cfg_column_name)
                        cfg_width = c_d["CfgColumnDescription"].get("width")
                        if cfg_width is not None:
                            nctable._column_format[cfg_column_name]["width"] = cfg_width
                            if nctable._column_format[cfg_column_name]["end"] != -1:
                                nctable._column_format[cfg_column_name]["end"] = (
                                    nctable.get_column_start(cfg_column_name) + cfg_width
                                )
                        nctable.update_column_format(cfg_column_name, c_d["CfgColumnDescription"])
        except UnicodeDecodeError as exc:
            logger.error("File has invalid utf-8 encoding")
            raise exc
        return nctable

    @staticmethod
    def parse_table_description(lines: List[str]) -> Dict[str, Any]:
        """Parse a table description section from the header into config data.

        :param lines: lines from the table description header section
        :type lines: list[str]

        :returns: parsed nested dictionary representation of the table description
        :rtype: dict
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
    def parse_table_structure(lines: List[str]) -> Dict[str, Any]:
        """Parse the old-style table structure header into config data.

        :param lines: lines from #STRUCTBEGIN/#STRUCTEND table description block
        :type lines: list[str]

        :returns: parsed `TableDescription` config dict
        :rtype: dict
        """
        config_data = {}
        config_data["TableDescription"] = dict()
        config_data["TableDescription"]["columns"] = list()
        current_obj = None

        for line in lines:
            if line.startswith("NAME = "):
                if current_obj is not None:
                    config_data["TableDescription"]["columns"].append(current_obj)
                current_obj = {}
                current_obj["CfgColumnDescription"] = dict()
                current_obj["CfgColumnDescription"]["key"] = line.split("=")[1].strip()
            elif line.startswith("TYPE = "):
                type_str = line.split("=")[1].strip()
                if type_str == "N":
                    current_obj["CfgColumnDescription"]["unit"] = "FLOAT"
                elif type_str == "C":
                    current_obj["CfgColumnDescription"]["unit"] = "INT"
                else:
                    raise NotImplementedError("type not implemented '%s'", line)
            elif line.startswith("WIDTH = "):
                current_obj["CfgColumnDescription"]["width"] = int(line.split("=")[1].strip()) + 1
            elif line.startswith("DEC = "):
                current_obj["CfgColumnDescription"]["decimals"] = int(line.split("=")[1].strip())
            elif line.startswith("DIA-"):
                pass
            elif line.startswith("#STRUCTBEGIN"):
                pass
            elif line.startswith("#STRUCTEND"):
                config_data["TableDescription"]["columns"].append(current_obj)
            elif line.startswith("*"):
                pass
            else:
                raise NotImplementedError("no pattern for line '%s'", line)

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
            for column, config in json_data["column_config"].items():
                logger.debug(
                    "add column %s [%d:%d]",
                    column,
                    config["start"],
                    config["end"],
                )
                nct.append_column(
                    name=column,
                    start=config["start"],
                    end=config["end"],
                )
                if "empty_value" in config:
                    nct.set_column_empty_value(column, config["empty_value"])
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
