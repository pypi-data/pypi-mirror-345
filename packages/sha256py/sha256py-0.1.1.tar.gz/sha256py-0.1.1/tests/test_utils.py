import os
import tempfile
import pytest
from sha256py.utils import read_file_input
from sha256py.core import Sha256
import hashlib

def test_file_input():
    content = "File test string"
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as f:
        f.write(content)
        f.flush()
        path = f.name

    try:
        read = read_file_input(path)
        assert read == content
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert Sha256(read).hexdigest() == expected
    finally:
        os.remove(path)

def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_file_input("this_file_should_not_exist.txt")
