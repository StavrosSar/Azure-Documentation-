from pathlib import Path
import pytest

from doc2json.cli import resolve_input_file


def test_resolve_input_file_exact_path(tmp_path: Path):
    f = tmp_path / "invoice1.pdf"
    f.write_bytes(b"%PDF-1.4 dummy")
    assert resolve_input_file(str(f)) == str(f)


def test_resolve_input_file_adds_extension(tmp_path: Path):
    # pass without extension; resolver should find .png (or any supported ext)
    f = tmp_path / "invoiceX.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\n dummy")
    assert resolve_input_file(str(tmp_path / "invoiceX")) == str(f)


def test_resolve_input_file_raises_when_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        resolve_input_file(str(tmp_path / "does_not_exist"))
