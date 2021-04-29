#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path


class TableReader():
    """generic parser for table files commonly used by TNC, iTNC, CNCPILOT and MANUALplus controls"""

    def __init__(self):
        """init object variables logging"""
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.name = None
        self.suffix = None
        self.version = None
        self.has_unit = False
        self.is_metric = False

    def parse_table(self, table_path):
        """Parse a file of one of the common table formats

        :param str or Path table_path: Path to the table file

        :returns: list od dictionarys. key is the column name, value the content of the table cell
        :rtype: list
        """
        self.name = None
        self.suffix = None
        self.version = None
        self.has_unit = False
        self.is_metric = False

        table_file = Path(table_path)
        if not table_file.is_file():
            raise FileNotFoundError('Could not open file %s' % table_path)

        with table_file.open(mode='r') as tfp:
            header_line = tfp.readline().strip()
            logging.debug('Checking line for header: %s', header_line)
            header = re.match(
                r"^BEGIN (?P<name>[A-Z_ 0-9]*)\.(?P<suffix>[A-Z0-9]{1,4})(?P<unit> MM| INCH)?(?: Version: \'Update:(?P<version>\d+\.\d+)\')?$", header_line)

            if header is None:
                raise Exception(
                    'File has wrong format: incorrect header for file %s' % table_path)

            self.name = header.group('name').strip()
            self.suffix = header.group('suffix')
            self.version = header.group('version')

            if header.group('unit') is not None:
                self.has_unit = True
                if 'MM' in header.group('unit'):
                    self.is_metric = True
                    logging.debug(
                        'Header Infomation for file "%s" Name "%s", file is metric, Version: "%s"', table_file, self.name, self.version)
                else:
                    self.is_metric = False
                    logging.debug(
                        'Header Infomation for file "%s" Name "%s", file is inch, Version: "%s"', table_file, self.name, self.version)
            else:
                self.has_unit = False
                self.is_metric = False
                logging.debug('Header Infomation for file "%s" Name "%s", file has no units, Version: "%s"',
                              table_file, self.name, self.version)

            next_line = tfp.readline()
            if '#STRUCTBEGIN' in next_line or 'TableDescription' in next_line:
                in_preamble = True
                next_line = tfp.readline()
                while in_preamble:
                    if next_line.startswith('#'):
                        in_preamble = False
                    elif next_line.startswith(')'):
                        in_preamble = False
                    else:
                        next_line = tfp.readline()
                next_line = tfp.readline()

            column_header = next_line
            column_list = list()
            column_pattern = re.compile(r"([A-Za-z-12\.]+)(?:\s+)")
            for column_match in column_pattern.finditer(column_header):
                column_list.append({'start': column_match.start(
                ), 'end': column_match.end()-1, 'name': column_match.group().strip()})

            logging.debug('Found %d columns', len(column_list))

            table_content = list()

            for line in tfp.readlines():
                if line.startswith('[END]'):
                    break

                table_entry = dict()

                for column in column_list:
                    table_entry[column['name']
                                ] = line[column['start']:column['end']].strip()
                table_content.append(table_entry)

            logging.debug('Found %d entrys', len(table_content))
        return table_content

    @staticmethod
    def format_entry_float(str_value):
        """convert the string value o a table cell to float value"""
        str_value = str_value.strip()
        if str_value == '-' or len(str_value) == 0:
            return None

        return float(str_value)

    @staticmethod
    def format_entry_int(str_value):
        """convert the string value o a table cell to int value"""
        str_value = str_value.strip()
        if str_value == '-' or len(str_value) == 0:
            return None

        return int(str_value)

    @staticmethod
    def format_entry_bool(str_value):
        """convert the string value o a table cell to boolean value"""
        str_value = str_value.strip()
        if len(str_value) == 0:
            return None
        elif str_value == '1':
            return True

        return False
