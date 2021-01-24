#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from pathlib import Path


class TableReader():

    def __init__(self, table_path):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

        table_file = Path(table_path)
        if not table_file.is_file():
            raise FileNotFoundError('Could not open file %s' % table_path)

        with table_file.open(mode='r') as tfp:
            header_line = tfp.readline().strip()

            header = re.match(
                r"^BEGIN ([A-Z]*)\.([A-Z]{1,3}) (MM|INCH)(?: Version: \'Update:(\d+\.\d+)\')?$",
                header_line)

            if header is None:
                raise Exception(
                    'File has wrong format: incorrect header for file %s' % table_path)

            self._name = header.group(1)
            if 'MM' in header.group(3):
                self._is_metric = True
            else:
                self._is_metric = False

            self._version = header.group(4)

            logging.debug('Header Infomation for file %s Name %s, file is metric %s, Version %s',
                          table_file, self._name, self._is_metric, self._version)

            column_header = tfp.readline()

            column_list = list()
            column_pattern = re.compile(r"([A-Z-12\.]+)(?:\s+)")
            for column_match in column_pattern.finditer(column_header):
                column_list.append({'start': column_match.start(
                ), 'end': column_match.end()-1, 'name': column_match.group().strip()})

            logging.debug('Found %d columns', len(column_list))

            self._table_content = list()

            for line in tfp.readlines():
                if line.startswith('[END]'):
                    break

                table_entry = dict()

                for column in column_list:
                    table_entry[column['name']
                                ] = line[column['start']:column['end']].strip()
                self._table_content.append(table_entry)

            logging.debug('Found %d entrys', len(self._table_content))


class ToolTable(TableReader):
    COLUMN_TITLE_NR = 'T'
    COLUMN_TITLE_NAME = 'NAME'
    COLUMN_TITLE_LENGTH = 'L'
    COLUMN_TITLE_RADIUS = 'R'
    COLUMN_TITLE_TIP_RADIUS = 'R2'
    COLUMN_TITLE_LENGTH_DELTA = 'DL'
    COLUMN_TITLE_RADIUS_DELTA = 'DR'
    COLUMN_TITLE_TIP_RADIUS_DELTA = 'DR2'
    COLUMN_TITLE_DOC = 'DOC'

    # COLUMN_TITLE_ = ''

    def __init__(self, table_path):
        super().__init__(table_path)
        for tool in self._table_content:
            print(tool[ToolTable.COLUMN_TITLE_NAME])



if __name__ == '__main__':
    logging.basicConfig(
        format='%(name)s  %(levelname)s : %(message)s', level=logging.DEBUG)
    ToolTable('../data/tool.t')
    # ToolTable('../data/tool 2.t')
    # ToolTable('../data/tool 3.t')
    # ToolTable('../data/TOOL 4.t')
    # ToolTable('../data/TOOL 5.t')
    # ToolTable('../data/TOOL 6.t')
    # ToolTable('../data/TOOL 7.t')
    # ToolTable('../data/tool.t.bak')
    # ToolTable('../data/tool.t.bak 2')
