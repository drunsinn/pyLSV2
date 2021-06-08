#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script lets you use some of the functions included in pyLSV2 via
   the command line.
"""
import logging
import argparse
import re
from pathlib import Path

import pyLSV2

REMOTE_PATH_REGEX = r"(?P<prot>lsv2)://(?P<host>.*?)(?::(?P<port>\d{1,5}))?/(?P<drive>TNC|PLC|SYS):(?P<path>[/A-Za-z\d\.\*_-]{2,})"
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='command line script for functions in pyLSV2')
    parser.add_argument("source", help='souce file', type=str)
    parser.add_argument("destination", help="destination file or path", type=str)
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument("-d", "--debug", help='enable log level DEBUG',
                           action="store_const", dest="loglevel", const=logging.DEBUG,
                           default=logging.WARNING)
    log_group.add_argument("-v", "-verbose", help='enable log level INFO',
                           action="store_const", dest="loglevel", const=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    logging.debug('Start logging with level "%s"', logging.getLevelName(args.loglevel))

    source_is_remote = False
    dest_is_remote = False

    host_machine = None
    host_port = None
    use_ssh = False

    source_match = re.match(REMOTE_PATH_REGEX, args.source)
    if source_match is not None:
        source_is_remote = True
        source_path = source_match.group("drive") + ":" + source_match.group("path")
        host_machine = source_match.group("host")
        host_port = int(source_match.group("port"))
        if source_match.group("prot") == 'ssh':
            use_ssh = True
        logging.info('Source path %s is on remote %s:%d via %s',
                      source_path, host_machine, host_port, source_match.group("prot"))
    else:
        source_path = Path(args.source)
        logging.info('Source path %s is local',
                      source_path.resolve())
    

    dest_match = re.match(REMOTE_PATH_REGEX, args.destination)
    if dest_match is not None:
        dest_is_remote = True
        dest_path = dest_match.group("drive") + ":" + dest_match.group("path")

        if source_is_remote and host_machine == dest_match.group("host"):
            logging.error('Cant copy between different remotes "%s" and "%s"',
                          host_machine,
                          dest_match.group("host"))
            exit(-1)
        
        host_machine = dest_match.group("host")
        host_port = int(dest_match.group("port"))
        if dest_match.group("prot") == 'ssh':
            use_ssh = True
        logging.info('Destination path %s is on remote %s:%d via %s',
                      dest_path, host_machine, host_port, dest_match.group("prot"))
    else:
        dest_path = Path(args.destination)
        logging.info('Destination path %s is local',
                      dest_path.resolve())
