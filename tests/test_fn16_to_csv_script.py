import csv
import pathlib
import tempfile

from pyLSV2.scripts.fn16_to_csv import convert_fn16_output_to_csv


def test_convert_fn16_output_to_csv():
    format_content = '"Status: %02d, Name: %15s", Q1111, QS3;\nM_CLOSE;\n'
    output_content = "Status: 42, Name:          Alice\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        format_path = tmp_path / "format.txt"
        output_path = tmp_path / "output.txt"
        csv_path = tmp_path / "output.csv"

        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        convert_fn16_output_to_csv(format_path, output_path, csv_path)

        assert csv_path.is_file()

        with csv_path.open(encoding="utf-8", newline="") as csv_fp:
            reader = csv.reader(csv_fp)
            rows = list(reader)

        assert rows[0] == ["Q1111", "QS3"]
        assert rows[1] == ["42", "Alice"]


def test_convert_fn16_output_to_csv_merges_block_data_events():
    format_content = '"%02d", DAY;\n"%02d", MONTH;\nM_CLOSE;\n'
    output_content = "30\n05\n"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        format_path = tmp_path / "format.txt"
        output_path = tmp_path / "output.txt"
        csv_path = tmp_path / "output.csv"

        format_path.write_text(format_content, encoding="utf-8")
        output_path.write_text(output_content, encoding="utf-8")

        convert_fn16_output_to_csv(format_path, output_path, csv_path)

        with csv_path.open(encoding="utf-8", newline="") as csv_fp:
            reader = csv.reader(csv_fp)
            rows = list(reader)

        assert rows[0] == ["DAY", "MONTH"]
        assert rows[1] == ["30", "5"]
