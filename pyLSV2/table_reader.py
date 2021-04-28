#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path


class TableReader():
    """generic parser for table files commonly used by TNC and iTNC controls"""

    def __init__(self, table_path):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        table_file = Path(table_path)
        if not table_file.is_file():
            raise FileNotFoundError('Could not open file %s' % table_path)

        with table_file.open(mode='r') as tfp:
            header_line = tfp.readline().strip()
            logging.debug('Checking line for header: %s', header_line)
            header = re.match(r"^BEGIN (?P<name>[A-Z_ 0-9]*)\.(?P<suffix>[A-Z0-9]{1,4})(?P<unit> MM| INCH)?(?P<version> Version: \'Update:(\d+\.\d+)\')?$", header_line)

            if header is None:
                raise Exception('File has wrong format: incorrect header for file %s' % table_path)

            self._name = header.group('name').strip()
            self._suffix = header.group('suffix')
            self._version = header.group('version')
            
            if header.group('unit') is not None:
                self._has_unit = True
                if 'MM' in header.group('unit'):
                    self._is_metric = True
                    logging.debug('Header Infomation for file "%s" Name "%s", file is metric, Version: "%s"', table_file, self._name, self._version)
                else:
                    self._is_metric = False
                    logging.debug('Header Infomation for file "%s" Name "%s", file is inch, Version: "%s"', table_file, self._name, self._version)
            else:
                self._has_unit = False
                self._is_metric = None
                logging.debug('Header Infomation for file "%s" Name "%s", file has no units, Version: "%s"', table_file, self._name, self._version)

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
                column_list.append({'start': column_match.start(), 'end': column_match.end()-1, 'name': column_match.group().strip()})

            logging.debug('Found %d columns', len(column_list))

            self._table_content = list()

            for line in tfp.readlines():
                if line.startswith('[END]'):
                    break

                table_entry = dict()

                for column in column_list:
                    table_entry[column['name']] = line[column['start']:column['end']].strip()
                self._table_content.append(table_entry)

            logging.debug('Found %d entrys', len(self._table_content))


class ToolEntry():
    number = None
    name = None
    lenght = None
    radius = None
    tip_radius = None
    delta_length = None
    delta_radius = None
    delta_tip_radius = None
    docstring = None


class ToolTable(TableReader):
    COLUMN_TITLE_NR = 'T'
    COLUMN_TITLE_NAME = 'NAME'
    COLUMN_TITLE_LENGTH = 'L'
    COLUMN_TITLE_RADIUS = 'R'
    COLUMN_TITLE_TIP_RADIUS = 'R2'
    COLUMN_TITLE_DELTA_LENGTH = 'DL'
    COLUMN_TITLE_DELTA_RADIUS = 'DR'
    COLUMN_TITLE_DELTA_TIP_RADIUS = 'DR2'
    COLUMN_TITLE_DOC = 'DOC'

    # COLUMN_TITLE_ = ''

    def __init__(self, table_path):
        super().__init__(table_path)

        if len(self._table_content) < 1:
            logging.error('Table is empty')
            return None

        logging.debug('Found Columns: %s', self._table_content[0].keys())

        tools = list()

        for entry in self._table_content:
            t = ToolEntry()
            t.number = entry[ToolTable.COLUMN_TITLE_NR]
            t.name = entry[ToolTable.COLUMN_TITLE_NAME]
            t.lenght = entry[ToolTable.COLUMN_TITLE_LENGTH]
            t.radius = entry[ToolTable.COLUMN_TITLE_RADIUS]
            t.tip_radius = entry[ToolTable.COLUMN_TITLE_TIP_RADIUS]
            t.delta_length = entry[ToolTable.COLUMN_TITLE_DELTA_LENGTH]
            t.delta_radius = entry[ToolTable.COLUMN_TITLE_DELTA_RADIUS]
            t.delta_tip_radius = entry[ToolTable.COLUMN_TITLE_DELTA_TIP_RADIUS]
            tools.append(t)

        logging.info('Found %d tool entries in table %s', len(tools), table_path)
