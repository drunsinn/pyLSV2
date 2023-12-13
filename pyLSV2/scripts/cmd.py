#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This script lets you use some of the functions included in pyLSV2 via
   the command line.
"""
import os
import sys
import logging
import argparse
import re
import socket

import pyLSV2

__author__ = "drunsinn"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "dr.unsinn@googlemail.com"

REMOTE_PATH_REGEX = (
    r"^(?P<prot>lsv2(\+ssh)?):\/\/(?P<host>[\w\.-]*)(?::(?P<port>\d{2,5}))?(?:\/(?P<drive>(TNC|PLC):))(?P<path>(\/[\$\.\w\d_-]+)*)\/?$"
)


def main():
    parser = argparse.ArgumentParser(description="command line script for functions in pyLSV2")
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
        default=logging.WARNING,
    )

    parser.add_argument("-t", "--timeout", help="timeout duration in seconds", type=float, default=10.0)
    parser.add_argument(
        "-f",
        "--force",
        help="replace file at target if it already exists",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    logger = logging.getLogger("lsv2cmd")

    logger.debug("Start logging with level '%s'", logging.getLevelName(args.loglevel))
    logger.debug("Source Path: %s", args.source)
    logger.debug("Destination Path: %s", args.destination)

    source_is_remote = False
    dest_is_remote = False

    host_machine = ""
    host_port = 19000
    use_ssh = False

    source_path = ""
    dest_path = ""

    source_match = re.match(REMOTE_PATH_REGEX, args.source)
    logger.debug("result of regex for source: %s", source_match)

    if source_match is not None:
        source_is_remote = True
        source_path = source_match.group("drive") + source_match.group("path")
        host_machine = str(source_match.group("host"))
        if source_match.group("port") is not None:
            host_port = int(source_match.group("port"))
        if "ssh" in source_match.group("prot"):
            use_ssh = True
        logger.info(
            "Source path %s is on remote %s:%d via %s",
            source_path,
            host_machine,
            host_port,
            source_match.group("prot"),
        )
    else:
        source_path = args.source
        logger.info("Source path %s is local", os.path.abspath(source_path))

    dest_match = re.match(REMOTE_PATH_REGEX, args.destination)
    logger.debug("result of regex for destination: %s", dest_match)

    if dest_match is not None:
        dest_is_remote = True
        dest_path = dest_match.group("drive") + dest_match.group("path")
        if source_is_remote and host_machine != dest_match.group("host"):
            logger.error(
                "Can't copy between different remotes '%s' and '%s'",
                host_machine,
                dest_match.group("host"),
            )
            sys.exit(-1)

        host_machine = str(dest_match.group("host"))
        if dest_match.group("port") is not None:
            host_port = int(dest_match.group("port"))
        if "ssh" in dest_match.group("prot"):
            use_ssh = True
        logger.info(
            "Destination path %s is on remote %s:%s via %s",
            dest_path,
            host_machine,
            host_port,
            dest_match.group("prot"),
        )
    else:
        dest_path = args.destination
        logger.info("Destination path %s is local", os.path.abspath(dest_path))

    if use_ssh:
        import sshtunnel

        ssh_forwarder = sshtunnel.SSHTunnelForwarder(host_machine, remote_bind_address=("127.0.0.1", host_port))
        ssh_forwarder.start()
        host_machine = "127.0.0.1"
        host_port = ssh_forwarder.local_bind_port
        logger.info("SSH tunnel established. local port is %d", host_port)

    try:
        con = pyLSV2.LSV2(hostname=host_machine, port=host_port, timeout=args.timeout)
        con.connect()
    except socket.gaierror as ex:
        logger.error("An Exception occurred: '%s'", ex)
        logger.error("Could not resolve host information: '%s'", host_machine)
        sys.exit(-2)

    if source_is_remote:
        file_info = con.file_info(remote_file_path=str(source_path))
        if not file_info:
            logger.error("source file dose not exist on remote: '%s'", source_path)
            sys.exit(-3)
        elif file_info.is_directory or file_info.is_drive:
            logger.error("source on remote is not file but directory: '%s'", source_path)
            sys.exit(-4)
    else:
        if os.path.exists(source_path):
            logger.debug("source file exists")
        else:
            if os.path.isfile(source_path):
                logger.error("source file dose not exist: '%s'", source_path)
                sys.exit(-5)
            else:
                logger.error("source folder dose not exist: '%s'", source_path)
                sys.exit(-6)

    success = False
    if source_is_remote and dest_is_remote:
        logger.debug("Local copy on remote")
        success = con.copy_remote_file(source_path=source_path, target_path=dest_path)
    elif source_is_remote and not dest_is_remote:
        logger.debug("copy from remote to local")
        success = con.recive_file(remote_path=source_path, local_path=dest_path, override_file=args.force)
    else:
        logger.debug("copy from local to remote")
        success = con.send_file(local_path=source_path, remote_path=dest_path, override_file=args.force)
    con.disconnect()

    if success:
        logger.info("File copied successful")
        sys.exit(0)
    sys.exit(-10)


if __name__ == "__main__":
    main()
