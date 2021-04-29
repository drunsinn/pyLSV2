
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import pathlib
from pyLSV2 import TableReader

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":

    data_dir = pathlib.Path('../data/')

    for subfolder in ('table_itnc530', 'table_pilot640', 'table_tnc640'):

        current_folder = data_dir.joinpath(subfolder)

        for table_path in current_folder.glob('*.*'):
            tr = TableReader()
            tr.parse_table(table_path)
