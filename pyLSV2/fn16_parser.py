#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""module with reader for files that where generated with FN16"""

from dataclasses import dataclass
from pathlib import Path
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class InstructionKind(Enum):
    CONTROL = "control"
    LANGUAGE = "language"
    FORMAT = "format"
    TEXT = "text"


SPEC_PATTERN = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?(?:D|F|I|S|RS)", re.IGNORECASE)
SPEC_PARSE_PATTERN = re.compile(
    r"%(?P<flags>[-+ #0]*)(?P<width>\d+)?(?:\.(?P<precision>\d+))?(?P<type>D|F|I|S|RS)$",
    re.IGNORECASE,
)


@dataclass
class FN16Instruction:
    """Representation of one FN16 format instruction."""

    kind: InstructionKind
    raw: str
    specs: Optional[List[str]] = None
    variables: Optional[List[str]] = None


@dataclass
class FN16Event:
    """Represents one parsed FN16 event from the output file."""

    type: str
    raw: Optional[str] = None
    values: Optional[Dict[str, Any]] = None
    command: Optional[str] = None


@dataclass
class FN16Block:
    """Container for events that belong to a single FN16 block."""

    block_id: int
    events: List[FN16Event]


@dataclass
class FN16Document:
    """Document containing one or more parsed FN16 blocks."""

    blocks: List[FN16Block]


class FN16Parser:
    """Parser for FN16 format files and FN16 output files."""

    def __init__(self, format_file: Union[str, Path]):
        """Create a parser and load the FN16 format definition."""
        self.instructions = FN16Parser.parse_format_file(format_file)

    @staticmethod
    def parse_format_file(path: Union[str, Path]) -> List[FN16Instruction]:
        """Parse an FN16 format file and return the list of instructions."""
        instructions: List[FN16Instruction] = []
        file_path = Path(path)

        with file_path.open(encoding="utf-8") as infile:
            for line in infile:
                line = line.rstrip("\r\n")
                stripped_line = line.strip()
                if not stripped_line or stripped_line.startswith("*"):
                    continue

                # Remove inline comments after the end-of-command semicolon.
                line = re.sub(r"\s*;\s*\*.*$", ";", line)
                if line.rstrip().endswith(";"):
                    line = line.rstrip()
                    line = line[:-1].rstrip()

                if not line:
                    continue

                stripped_line = line.strip()

                if stripped_line.startswith("M_"):
                    instructions.append(FN16Instruction(kind=InstructionKind.CONTROL, raw=stripped_line.rstrip(";")))
                    continue

                if stripped_line.startswith("L_"):
                    instructions.append(FN16Instruction(kind=InstructionKind.LANGUAGE, raw=stripped_line.rstrip(";")))
                    continue

                if stripped_line.startswith('"'):
                    match = re.match(r'^"(?P<text>(?:\\.|[^"\\])*)"(?:\s*,\s*(?P<variables>.*))?$', stripped_line)
                    if not match:
                        continue

                    text = match.group("text")
                    specs = SPEC_PATTERN.findall(text)
                    variables: List[str] = []

                    variable_part = match.group("variables")
                    if specs and variable_part:
                        variables = [v.strip() for v in variable_part.rstrip(";").split(",") if v.strip()]

                    instructions.append(
                        FN16Instruction(
                            kind=InstructionKind.FORMAT if specs else InstructionKind.TEXT,
                            raw=text,
                            specs=specs,
                            variables=variables,
                        )
                    )

        return instructions

    def is_block_end_command(self, command: str) -> bool:
        """Check if a command ends the current block."""
        return command.startswith("M_CLOSE") or command.startswith("M_APPEND") or command.startswith("M_TRUNCATE")

    def spec_to_regex(self, spec: str) -> str:
        """Convert an FN16 format specifier into a regular expression group."""
        match = SPEC_PARSE_PATTERN.match(spec)
        if not match:
            return r"(.+?)"

        width = match.group("width")
        type_code = match.group("type")
        normalized_type = type_code.upper()

        if type_code in ("d", "i", "I"):
            if width:
                return r"\s*([+-]?\d{%s})\s*" % width
            return r"\s*([+-]?\d+)\s*"

        if normalized_type in ("D", "F"):
            number = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?"
            return r"\s*(%s)\s*" % number

        if normalized_type in ("S", "RS"):
            if width:
                return r"\s*(.{1,%s}?)\s*" % width
            return r"\s*(.+?)\s*"

        return r"(.+?)"

    def build_regex(self, format_text: str) -> re.Pattern:
        """Build a regex pattern from FN16 format text and its specifiers."""
        parts = re.split(r"(" + SPEC_PATTERN.pattern + ")", format_text, flags=re.IGNORECASE)
        regex = ""

        for part in parts:
            if SPEC_PATTERN.fullmatch(part):
                regex += self.spec_to_regex(part)
            else:
                literal = part.replace("%%", "%").replace('%\\"', '"').replace("\\\\", "\\").replace("\\n", "\n")
                regex += "".join(r"\s+" if char.isspace() else re.escape(char) for char in literal)

        return re.compile(f"^{regex}$")

    def parse_output(self, output_file: Union[str, Path]) -> FN16Document:
        """Parse FN16 output text into blocks and events according to the loaded format."""
        file_path = Path(output_file)
        blocks: List[FN16Block] = []
        block_counter = 1

        with file_path.open(encoding="utf-8") as infile:
            lines = [line.rstrip("\n") for line in infile]

        line_index = 0
        while line_index < len(lines):
            current_events: List[FN16Event] = []
            empty_hide = False
            block_closed = False

            for instr in self.instructions:
                if instr.kind in (InstructionKind.CONTROL, InstructionKind.LANGUAGE):
                    current_events.append(FN16Event(type="context", command=instr.raw))

                    if instr.raw.startswith("M_EMPTY_HIDE"):
                        empty_hide = True
                    elif instr.raw.startswith("M_EMPTY_SHOW"):
                        empty_hide = False

                    if self.is_block_end_command(instr.raw):
                        blocks.append(FN16Block(block_id=block_counter, events=current_events))
                        block_counter += 1
                        block_closed = True

                        if instr.raw.startswith(("M_CLOSE", "M_TRUNCATE")):
                            return FN16Document(blocks=blocks)
                        break

                    continue

                if line_index >= len(lines):
                    break

                line_count = 1
                if instr.kind in (InstructionKind.TEXT, InstructionKind.FORMAT):
                    decoded_text = instr.raw.replace("%%", "%").replace('%\\"', '"').replace("\\\\", "\\").replace("\\n", "\n")
                    line_count = decoded_text.count("\n") + 1
                line = "\n".join(lines[line_index : line_index + line_count])
                line_index += line_count

                if instr.kind == InstructionKind.TEXT:
                    current_events.append(FN16Event(type="text", raw=line))
                    continue

                if instr.kind == InstructionKind.FORMAT:
                    if empty_hide and not line.strip():
                        continue

                    regex = self.build_regex(instr.raw)
                    match = regex.match(line)
                    values: Dict[str, Any] = {}

                    if match and instr.variables and instr.specs:
                        for index, var in enumerate(instr.variables):
                            raw_value = match.group(index + 1)
                            spec = instr.specs[index]

                            type_code = spec[-1]
                            if type_code in ("d", "i", "I"):
                                values[var] = int(raw_value)
                            elif type_code in ("D", "F", "f"):
                                values[var] = float(raw_value)
                            else:
                                values[var] = raw_value.strip()

                    current_events.append(FN16Event(type="data", raw=line, values=values))

            if not block_closed and current_events:
                blocks.append(FN16Block(block_id=block_counter, events=current_events))
                break

        return FN16Document(blocks=blocks)
