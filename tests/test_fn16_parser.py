import pathlib
import tempfile

import pyLSV2
from pyLSV2.fn16_parser import FN16Parser, InstructionKind


def test_parse_format_file():
    content = """
    * Comment line
    L_LANGUAGE;
    "Datum: %02d.%02d.%04d", DAY, MONTH, YEAR4;
    "Value1: %d, Value2: %f", Q123, QL456;
    "Sting without variables";
    "String vairable %s", QS1; * with comment
    "Sting without variables"; * with comment
    M_EMPTY_HIDE;
    M_APPEND;
    M_TRUNCATE;
    M_APPEND_MAX20;
    M_CLOSE;
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        format_path.write_text(content, encoding="utf-8")

        instructions = FN16Parser.parse_format_file(format_path)

        assert len(instructions) == 11
        assert instructions[0].kind == InstructionKind.LANGUAGE
        assert instructions[1].kind == InstructionKind.FORMAT
        assert instructions[1].variables == ["DAY", "MONTH", "YEAR4"]
        assert instructions[2].kind == InstructionKind.FORMAT
        assert instructions[2].variables == ["Q123", "QL456"]
        assert instructions[3].kind == InstructionKind.TEXT
        assert instructions[3].raw == "Sting without variables"
        assert instructions[4].kind == InstructionKind.FORMAT
        assert instructions[4].variables == ["QS1"]
        assert instructions[5].kind == InstructionKind.TEXT
        assert instructions[5].raw == "Sting without variables"
        assert instructions[6].kind == InstructionKind.CONTROL
        assert instructions[6].raw == "M_EMPTY_HIDE"
        assert instructions[7].kind == InstructionKind.CONTROL
        assert instructions[7].raw == "M_APPEND"
        assert instructions[8].kind == InstructionKind.CONTROL
        assert instructions[8].raw == "M_TRUNCATE"
        assert instructions[9].kind == InstructionKind.CONTROL
        assert instructions[9].raw == "M_APPEND_MAX20"
        assert instructions[10].kind == InstructionKind.CONTROL
        assert instructions[10].raw == "M_CLOSE"


def test_fn16_parser_output():
    format_content = '"Status: %02d, Name: %15s", Q1111, QS3;\nM_CLOSE;\n'
    output_content = "Status: 42, Name:          Alice\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        output_path = pathlib.Path(tmp_dir) / "output.txt"
        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        parser = FN16Parser(format_path)
        document = parser.parse_output(output_path)

        assert len(document.blocks) == 1
        block = document.blocks[0]
        assert len(block.events) == 2
        data_event = block.events[0]
        assert data_event.type == "data"
        assert data_event.values == {"Q1111": 42, "QS3": "Alice"}
        assert block.events[1].type == "context"
        assert block.events[1].command == "M_CLOSE"


def test_fn16_parser_importable():
    assert hasattr(pyLSV2, "FN16Parser")


def test_fn16_parser_multiline_with_append():
    """Test that M_APPEND allows multiple blocks with multiple lines each."""
    format_content = '"Data: %d", QL1;\n"Data2: %d", Q5;\nM_APPEND;'
    output_content = "Data: 100\nData2: 200\nData: 0\nData2: -1\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        output_path = pathlib.Path(tmp_dir) / "output.txt"
        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        parser = FN16Parser(format_path)
        document = parser.parse_output(output_path)

        assert len(document.blocks) == 2
        assert document.blocks[0].events[0].values == {"QL1": 100}
        assert document.blocks[0].events[1].values == {"Q5": 200}
        assert document.blocks[1].events[0].values == {"QL1": 0}
        assert document.blocks[1].events[1].values == {"Q5": -1}


def test_fn16_parser_padded_numeric_values():
    """Test that padded numeric FN16 output values are parsed correctly."""
    format_content = '"V1%f V2%15F V3%3.3f V4%1f V5%f V6%15f", Q1, Q2, Q3, Q4, Q5, Q6;\nM_CLOSE;\n'
    output_content = "V112.000000 V2      23.000000 V334.000 V445.000000 V556.000000 V6      67.000000\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        output_path = pathlib.Path(tmp_dir) / "output.txt"
        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        parser = FN16Parser(format_path)
        document = parser.parse_output(output_path)

        assert len(document.blocks) == 1
        data_event = document.blocks[0].events[0]
        assert data_event.values == {
            "Q1": 12.0,
            "Q2": 23.0,
            "Q3": 34.0,
            "Q4": 45.0,
            "Q5": 56.0,
            "Q6": 67.0,
        }


def test_fn16_parser_consecutive_widthed_integers():
    """Test that consecutive width-limited integer fields are parsed separately."""
    format_content = '"%02d%02d", DAY, MONTH;\nM_CLOSE;\n'
    output_content = "3005\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        output_path = pathlib.Path(tmp_dir) / "output.txt"
        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        parser = FN16Parser(format_path)
        document = parser.parse_output(output_path)

        assert len(document.blocks) == 1
        data_event = document.blocks[0].events[0]
        assert data_event.values == {"DAY": 30, "MONTH": 5}


def test_fn16_parser_manual_double_and_escaped_literals():
    format_content = '"Value: %D %% %\\" \\\\ %s", Q1, QS1;\nM_CLOSE;\n'
    output_content = 'Value: 1.25 % " \\ text\n'

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        output_path = pathlib.Path(tmp_dir) / "output.txt"
        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        document = FN16Parser(format_path).parse_output(output_path)

        assert document.blocks[0].events[0].values == {"Q1": 1.25, "QS1": "text"}


def test_fn16_parser_manual_escaped_line_break():
    format_content = '"First\\nSecond: %D", Q1;\nM_CLOSE;\n'
    output_content = "First\nSecond: 2.5\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        format_path = pathlib.Path(tmp_dir) / "format.txt"
        output_path = pathlib.Path(tmp_dir) / "output.txt"
        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        document = FN16Parser(format_path).parse_output(output_path)

        assert document.blocks[0].events[0].values == {"Q1": 2.5}
