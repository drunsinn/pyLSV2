#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ME101 data transfer interface"""

import argparse
from pathlib import Path
import logging
import re

try:
    import serial
except ImportError:
    raise SystemExit("Error: pyserial is not installed. Install with 'pip install pyserial'")

NULL = b"\x00"  # Null byte
DC1 = b"\x11"  # XON
DC3 = b"\x13"  # XOFF
EXT = b"\x03"  # End of Text
ESC = b"\x1b"  # Escape
LF = b"\x0a"  # Line Feed
CR = b"\x0d"  # Carriage Return

MAX_TAPE_BYTES = 45000  # Approximate maximum bytes that can fit on ME101 tape (45 KB)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ME101 transfer interface")

    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port (default: /dev/ttyUSB0)")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Verbosity (between 1-4 occurrences with more leading to more verbose logging). CRITICAL=0, ERROR=1, WARN=2, INFO=3, DEBUG=4",
    )
    subparsers = parser.add_subparsers(help="sub-command help", dest="cmd_mode")

    parser_a = subparsers.add_parser("read", help="Read programs from tape")
    parser_a.add_argument("-o", help="Output directory for read mode")

    parser_b = subparsers.add_parser("write", help="Write programs to tape")
    parser_b.add_argument("-i", "--input", nargs="+", type=argparse.FileType("r"), help="Input files for write mode")

    args = parser.parse_args()

    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARN,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    logging.basicConfig(level=log_levels[min(args.verbosity, max(log_levels.keys()))])

    try:
        rs232 = serial.Serial(
            port=args.port,
            baudrate=2400,
            bytesize=serial.SEVENBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            xonxoff=False,
            rtscts=False,
        )

        if args.cmd_mode == "write":
            logging.info("Starting write mode")
            # collect data
            data_to_send = b""
            for file in args.input:
                content = file.read()
                # replace \n with \r\n
                content = content.replace("\n", "\r\n")
                data_to_send += content.encode("ascii")
            logging.info(f"Collected data from {len(args.input)} files, total {len(data_to_send)} bytes")
            if len(data_to_send) > MAX_TAPE_BYTES:
                raise ValueError(f"Data to send ({len(data_to_send)} bytes) exceeds tape capacity ({MAX_TAPE_BYTES} bytes)")
            # Validate content
            for byte in data_to_send:
                if byte >= 128:
                    raise ValueError(f"Non-7bit ASCII character found in data: {byte} (0x{byte:02x})")
                if byte in {DC1, DC3, EXT, ESC}:
                    raise ValueError(f"Forbidden control character found in data: 0x{byte:02x}")
            # now, the protocol
            reply = rs232.read(1)
            while reply != DC1:
                logging.info("Waiting for DC1 (XON) from ME101")
                rs232.write(NULL)
                reply = rs232.read(1)
            for _ in range(20):
                rs232.write(NULL)
            reply = rs232.read(1)
            rs232.write(data_to_send)

            reply = rs232.read(1)
            logging.info("Sending End of Text")
            rs232.write(EXT)
        else:  # read file(s) from tape
            logging.info("Starting read mode")
            byte_data = bytearray()
            rs232.write(DC1)
            while True:
                new_char = rs232.read(1)

                if len(new_char) == 0:
                    continue

                if new_char > b"\x1b":
                    # print(new_data.decode('ascii', errors='ignore'))
                    byte_data.extend(new_char)
                else:
                    if new_char == ESC:
                        logging.info("Control character 'Escape' received, premature tape end or user abort")
                        break
                    elif new_char == EXT:
                        logging.info("Control character 'End of Text' received, transmission completed")
                        break
                    elif new_char in [LF, CR]:
                        byte_data.extend(new_char)
                    elif new_char == NULL:
                        pass
                    else:
                        raise NotImplementedError(f"received unexpected control data: '{new_char}'")

            new_char = rs232.read()
            if len(new_char) != 0:
                logging.warning(f"Received data after transfer finished: '{new_char}'")

            ascii_data = byte_data.decode("ascii", errors="ignore")
            logging.info(f"received {len(ascii_data)} ASCII characters")

            begin_found = False
            tape_content = dict()
            current_file = "_unknown_"
            tape_content[current_file] = list()
            for line in ascii_data.splitlines(keepends=False):
                if len(line) == 0:
                    continue
                # print(line)
                if (result := re.fullmatch(r"0 BEGIN PGM (?P<name>[\d\w]+) (?P<unit>MM|INCH) ?(?P<prot>P ?)?", line)) is not None:
                    if begin_found:
                        logging.warning("Found multiple BEGIN PGM lines, this should not happen")
                    else:
                        begin_found = True
                        current_file = result.group(1)
                        tape_content[current_file] = list()
                        logging.info(f"Found BEGIN line with filename: '{current_file}'")
                elif (result := re.fullmatch(r"\d+ END PGM (?P<name>[\d\w]+) (?P<unit>MM|INCH) ?(?P<prot>P ?)?", line)) is not None:
                    if not begin_found:
                        logging.warning(f"Found END PGM without BEGIN PGM for file {result.group(1)}")
                    else:
                        begin_found = False
                        logging.info(f"Found END line with filename: '{result.group(1)}'")
                tape_content[current_file].append(line)

            if len(tape_content["_unknown_"]) > 0:
                logging.warning("Content found outside of BEGIN/END blocks, stored under '_unknown_'")
            else:
                del tape_content["_unknown_"]

            logging.info(f"Programs found: {list(tape_content.keys())}")

            output_path = Path(args.o if args.o is not None else ".")
            if output_path.is_file():
                raise ValueError(f"Output path '{output_path}' is a file, but should be a directory")
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)

            for filename, content in tape_content.items():
                if len(content) == 0:
                    continue
                dest_path = output_path / f"{filename}.h"
                if dest_path.exists():
                    logging.warning(f"File '{dest_path}' already exists, overwriting")
                with open(dest_path, "w") as f:
                    f.write("\n".join(content))
                    f.write("\n")

    except serial.SerialException as e:
        logging.error(f"Serial port error: {e}")
    except PermissionError:
        logging.error("Permission denied - check user permissions")
    except FileNotFoundError:
        logging.error("Port not found - verify device connection")
    finally:
        if "set" in locals() and rs232.is_open:
            rs232.close()
