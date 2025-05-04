import hashlib
import subprocess
import sys
from pathlib import Path
from sha256py.cli import get_input_string, build_parser

def run_cli(args, input_data=None, binary=False):
    cmd = [sys.executable, "-m", "sha256py"] + args
    return subprocess.run(
        cmd,
        input=input_data if input_data else None,
        capture_output=True,
        text=not binary,
    )

def test_cli_basic_string():
    result = run_cli(["hello"])
    expected = hashlib.sha256(b"hello").hexdigest()
    assert expected in result.stdout

def test_cli_stdin():
    result = run_cli(["-"], input_data="from stdin")
    expected = hashlib.sha256(b"from stdin").hexdigest()
    assert expected in result.stdout

def test_cli_binary_output():
    result = run_cli(["test123", "--binary"])
    expected = hashlib.sha256(b"test123").digest()
    expected_bin = ''.join(f"{b:08b}" for b in expected)
    assert expected_bin in result.stdout

def test_cli_raw_output():
    result = run_cli(["test123", "--raw"], binary=True)
    expected = hashlib.sha256(b"test123").digest()
    assert result.stdout == expected

def test_cli_time_output():
    result = run_cli(["test123", "--time"])
    assert "Hash computed in" in result.stdout

def test_cli_file_input(tmp_path: Path):
    file = tmp_path / "sample.txt"
    file.write_text("hash me!")
    result = run_cli(["-f", str(file)])
    expected = hashlib.sha256(b"hash me!").hexdigest()
    assert expected in result.stdout

def test_cli_silent(monkeypatch):
    monkeypatch.setattr("sha256py.cli.getpass", lambda _: "silent input")
    from sha256py.cli import get_input_string, build_parser
    args = build_parser().parse_args(["--silent"])
    input_str = get_input_string(args)
    assert input_str == "silent input"

def test_cli_input_prompt(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "prompted input")
    args = build_parser().parse_args([])
    input_str = get_input_string(args)
    assert input_str == "prompted input"
