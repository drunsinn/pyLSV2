#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ME101 magnetic tape transfer interface for reading and writing programs."""

import argparse
import logging
import re
import sys
from pathlib import Path

try:
    import serial
except ImportError as e:
    raise SystemExit("Error: pyserial is not installed. Install with 'pip install pyserial'") from e

# ME101 Control Characters
NULL = b"\x00"  # Null byte
DC1 = b"\x11"  # XON (transmission on)
DC3 = b"\x13"  # XOFF (transmission off)
EXT = b"\x03"  # End of Text
ESC = b"\x1b"  # Escape
LF = b"\x0a"  # Line Feed
CR = b"\x0d"  # Carriage Return

# Maximum tape capacity (45 KB)
MAX_TAPE_BYTES = 45000

# Regex patterns for parsing tape content
BEGIN_PGM_PATTERN = r"0 BEGIN PGM (?P<name>[\d\w]+) (?P<unit>MM|INCH) ?(?P<prot>P ?)?"
END_PGM_PATTERN = r"\d+ END PGM (?P<name>[\d\w]+) (?P<unit>MM|INCH) ?(?P<prot>P ?)?"


def setup_logging(verbosity: int) -> None:
    """Configure logging based on verbosity level."""
    log_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    level = log_levels.get(min(verbosity, max(log_levels.keys())), logging.WARNING)
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def setup_serial_connection(port: str) -> serial.Serial:
    """Create and configure serial connection for ME101."""
    return serial.Serial(
        port=port,
        baudrate=2400,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
        xonxoff=False,
        rtscts=False,
    )


def validate_write_data(data: bytes) -> None:
    """Validate data before writing to tape."""
    if len(data) > MAX_TAPE_BYTES:
        raise ValueError(f"Data to send ({len(data)} bytes) exceeds tape capacity " f"({MAX_TAPE_BYTES} bytes)")

    forbidden_chars = {DC1, DC3, EXT, ESC}
    for byte in data:
        if byte >= 128:
            raise ValueError(f"Non-7bit ASCII character found: {byte} (0x{byte:02x})")
        if bytes([byte]) in forbidden_chars:
            raise ValueError(f"Forbidden control character found: 0x{byte:02x}")


def collect_input_data(input_files) -> bytes:
    """Read and prepare data from input files."""
    data = b""
    for file_obj in input_files:
        content = file_obj.read()
        # Normalize line endings to CR+LF (ME101 format)
        content = content.replace("\n", "\r\n")
        data += content.encode("ascii")
        data += NULL * 10  # Add padding between files

    logging.info(f"Collected data from {len(input_files)} files, total {len(data)} bytes")
    return data


def wait_for_xon(connection: serial.Serial) -> None:
    """Wait for DC1 (XON) signal from ME101."""
    while connection.read(1) != DC1:
        logging.debug("Waiting for DC1 (XON) from ME101")
        connection.write(NULL)


def send_write_handshake(connection: serial.Serial) -> None:
    """Send write mode handshake to ME101."""
    for _ in range(20):
        connection.write(NULL)
    connection.read(1)  # Read reply


def handle_write_mode(connection: serial.Serial, input_files) -> None:
    """Handle tape write operation."""
    logging.info("Starting write mode")

    data_to_send = collect_input_data(input_files)
    validate_write_data(data_to_send)

    wait_for_xon(connection)
    send_write_handshake(connection)
    connection.write(data_to_send)

    logging.info("Sending End of Text")
    connection.write(EXT)


def process_character(byte_data: bytearray, new_char: bytes) -> bool:
    """Process received character. Return True to stop reception."""
    if new_char > b"\x1b":
        byte_data.extend(new_char)
        return False

    if new_char == ESC:
        logging.info("Escape received: tape premature, user abort, or ME101 not ready")
        return True
    elif new_char == EXT:
        logging.info("End of Text received: transmission completed")
        return True
    elif new_char == DC3:
        logging.error("DC3 received: transmission interrupted by ME101 or STOP button")
        return True
    elif new_char in (LF, CR):
        byte_data.extend(new_char)
    elif new_char == NULL:
        pass  # Ignore null bytes
    else:
        raise NotImplementedError(f"Unexpected control character: 0x{new_char[0]:02x}")

    return False


def read_from_tape(connection: serial.Serial) -> bytes:
    """Read data from ME101 tape."""
    byte_data = bytearray()
    connection.write(DC1)

    while True:
        new_char = connection.read(1)
        if len(new_char) == 0:
            continue
        if process_character(byte_data, new_char):
            break

    trailing_data = connection.read()
    if trailing_data:
        logging.warning(f"Received unexpected data after transfer: {trailing_data}")

    return bytes(byte_data)


def parse_programs(tape_content: str) -> dict[str, list[str]]:
    """Parse program blocks from tape content."""
    programs = {}
    current_program = "_unknown_"
    programs[current_program] = []
    in_program = False

    for line in tape_content.splitlines():
        if not line:
            continue

        begin_match = re.fullmatch(BEGIN_PGM_PATTERN, line)
        if begin_match:
            if in_program:
                logging.warning("Found BEGIN without END: malformed tape content")
            current_program = begin_match.group("name")
            programs[current_program] = []
            in_program = True
            logging.info(f"Found program: {current_program}")
        else:
            end_match = re.fullmatch(END_PGM_PATTERN, line)
            if end_match:
                if not in_program:
                    logging.warning(f"Found END without BEGIN for: {end_match.group('name')}")
                in_program = False

        programs[current_program].append(line)

    # Clean up unknown programs
    if "_unknown_" in programs:
        if not programs["_unknown_"]:
            del programs["_unknown_"]

    return programs


def save_tape_content(output_dir: Path, tape_content: str) -> None:
    """Save raw tape content to file."""
    content_file = output_dir / "tapecontent.txt"
    if content_file.exists():
        logging.warning(f"Overwriting existing file: {content_file}")
    content_file.write_text(tape_content, encoding="ascii", errors="ignore")


def save_programs(output_dir: Path, programs: dict[str, list[str]]) -> None:
    """Save parsed programs to individual files."""
    for filename, content in programs.items():
        if not content:
            continue
        program_file = output_dir / f"{filename}.h"
        if program_file.exists():
            logging.warning(f"Overwriting existing file: {program_file}")
        program_file.write_text("\n".join(content) + "\n")


def handle_read_mode(connection: serial.Serial, output_dir: Path) -> None:
    """Handle tape read operation."""
    logging.info("Starting read mode")

    tape_bytes = read_from_tape(connection)
    tape_content = tape_bytes.decode("ascii", errors="ignore")
    logging.info(f"Received {len(tape_content)} ASCII characters")

    # Check if any data was received
    if not tape_content or tape_content.isspace():
        logging.warning("No data received from tape, aborting")
        return

    # Prepare output directory
    if output_dir.is_file():
        raise ValueError(f"Output path is a file, but should be a directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save content
    save_tape_content(output_dir, tape_content)
    programs = parse_programs(tape_content)
    logging.info(f"Programs found: {list(programs.keys())}")
    save_programs(output_dir, programs)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Create and configure command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="""ME101 magnetic tape transfer interface.

This script reads and writes programs to/from ME101 magnetic tape units via serial connection.

SETUP:
  1. Connect ME101 to computer via serial cable
  2. Configure serial port (default: /dev/ttyUSB0)
  3. Rewind tape if necessary
  4. Press TNC, READ and START on ME101 for reading or TNC and WRITE for writing

WRITE MODE:
  - Requires ASCII input files
  - Maximum 45 KB per tape side
  - Control characters (DC1, DC3, EXT, ESC) not allowed""",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--port",
        default="/dev/ttyUSB0",
        help="Serial port (default: /dev/ttyUSB0)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Verbosity: -v (ERROR), -vv (WARN), -vvv (INFO), -vvvv (DEBUG)",
    )

    subparsers = parser.add_subparsers(
        help="Operation mode",
        dest="cmd_mode",
        required=True,
    )

    read_parser = subparsers.add_parser("read", help="Read programs from tape")
    read_parser.add_argument(
        "-o",
        "--output",
        default=".",
        help="Output directory (default: current directory)",
    )

    write_parser = subparsers.add_parser("write", help="Write programs to tape")
    write_parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        type=argparse.FileType("r"),
        required=True,
        help="Input files to write to tape",
    )

    return parser


def main() -> None:
    """Main entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    setup_logging(args.verbosity)

    try:
        connection = setup_serial_connection(args.port)

        if args.cmd_mode == "write":
            handle_write_mode(connection, args.input)
        else:  # read mode
            output_path = Path(args.output) if hasattr(args, "output") else Path(".")
            handle_read_mode(connection, output_path)

    except serial.SerialException as e:
        logging.error(f"Serial port error: {e}")
        sys.exit(1)
    except PermissionError as e:
        logging.error(f"Permission denied: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logging.error(f"Port not found: {e}")
        sys.exit(1)
    except (ValueError, NotImplementedError) as e:
        logging.error(f"Invalid data: {e}")
        sys.exit(1)
    finally:
        if "connection" in locals() and connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
