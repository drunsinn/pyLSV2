#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script lets you use some of the functions included in pyLSV2 via
   the command line.
"""
import sys
import logging
import argparse
import re
import socket
from pathlib import Path

import pyLSV2

REMOTE_PATH_REGEX = r"^(?P<prot>lsv2):\/\/(?P<host>[\w\.]*)(?::(?P<port>\d{2,5}))?(?:\/(?P<drive>(TNC|PLC):))(?P<path>(\/[\$\.\w\d_-]+)*)\/?$"
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="command line script for functions in pyLSV2"
    )
    parser.add_argument(
        "source",
        help="source file. Either local path or URL with format lsv2://<hostname_or_ip>:<port>/TNC:/<path_to_file>",
        type=str,
    )
    parser.add_argument(
        "destination",
        help="destination file. Either local path or URL with format lsv2://<hostname_or_ip>:<port>/TNC:/<path_to_file>",
        type=str,
    )
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "-d",
        "--debug",
        help="enable log level DEBUG",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    log_group.add_argument(
        "-v",
        "--verbose",
        help="enable log level INFO",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )
    parser.add_argument(
        "-t", "--timeout", help="timeout duration in seconds", type=float, default=10.0
    )
    parser.add_argument(
        "-f",
        "--force",
        help="replace file at target if it already exists",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    logging.debug('Start logging with level "%s"', logging.getLevelName(args.loglevel))

    source_is_remote = False
    dest_is_remote = False

    host_machine = None
    host_port = 19000
    use_ssh = False

    source_match = re.match(REMOTE_PATH_REGEX, args.source)
    if source_match is not None:
        source_is_remote = True
        source_path = source_match.group("drive") + source_match.group("path")
        host_machine = source_match.group("host")
        if source_match.group("port") is not None:
            host_port = int(source_match.group("port"))
        if source_match.group("prot") == "ssh":
            use_ssh = True
        logging.info(
            "Source path %s is on remote %s:%d via %s",
            source_path,
            host_machine,
            host_port,
            source_match.group("prot"),
        )
    else:
        source_path = Path(args.source)
        logging.info("Source path %s is local", source_path.resolve())

    dest_match = re.match(REMOTE_PATH_REGEX, args.destination)
    if dest_match is not None:
        dest_is_remote = True
        dest_path = dest_match.group("drive") + dest_match.group("path")

        if source_is_remote and host_machine != dest_match.group("host"):
            logging.error(
                'Cant copy between different remotes "%s" and "%s"',
                host_machine,
                dest_match.group("host"),
            )
            sys.exit(-1)

        host_machine = dest_match.group("host")
        if dest_match.group("port") is not None:
            host_port = int(dest_match.group("port"))
        if dest_match.group("prot") == "ssh":
            use_ssh = True
        logging.info(
            "Destination path %s is on remote %s:%s via %s",
            dest_path,
            host_machine,
            host_port,
            dest_match.group("prot"),
        )
    else:
        dest_path = Path(args.destination)
        logging.info("Destination path %s is local", dest_path.resolve())

    if use_ssh:
        import sshtunnel

        ssh_forwarder = sshtunnel.SSHTunnelForwarder(
            host_machine, remote_bind_address=("127.0.0.1", host_port)
        )
        ssh_forwarder.start()
        host_machine = "127.0.0.1"
        host_port = ssh_forwarder.local_bind_port
        logging.info("SSH tunnel established. local port is %d", host_port)

    try:
        con = pyLSV2.LSV2(hostname=host_machine, port=host_port, timeout=args.timeout)
        con.connect()
    except socket.gaierror as ex:
        logging.error('An Exception occurred: "%s"', ex)
        logging.error('Could not resove host information: "%s"', host_machine)
        sys.exit(-2)

    if source_is_remote:
        file_info = con.get_file_info(remote_file_path=source_path)
        if not file_info:
            logging.error('source file dose not exist on remote: "%s"', source_path)
            sys.exit(-3)
        elif file_info["is_directory"]:
            logging.error(
                'source on remote is not file but directory: "%s"', source_path
            )
            sys.exit(-4)
    else:
        if not source_path.exists():
            if source_path.is_file():
                logging.error('source file dose not exist: "%s"', source_path)
                sys.exit(-5)
            else:  # source_path.is_dir():
                logging.error('source folder dose not exist: "%s"', source_path)
                sys.exit(-6)

    success = False
    if source_is_remote and dest_is_remote:
        logging.debug("Local copy on remote")
        success = con.copy_local_file(source_path=source_path, target_path=dest_path)
    elif source_is_remote and not dest_is_remote:
        logging.debug("copy from remote to this device")
        success = con.recive_file(
            remote_path=source_path, local_path=dest_path, override_file=args.force
        )
    else:
        logging.debug("copy from this device to remote")
        success = con.send_file(
            local_path=source_path, remote_path=dest_path, override_file=args.force
        )
    con.disconnect()

    if success:
        logging.info("File copied successful")
        sys.exit(0)
    sys.exit(-10)
