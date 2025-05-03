import hashlib

from sha256py.core import Sha256

def test_known_hash():
    input_str = "hello"
    expected = hashlib.sha256(input_str.encode()).hexdigest()
    assert Sha256(input_str).hexdigest() == expected

def test_empty_string():
    input_str = ""
    expected = hashlib.sha256(input_str.encode()).hexdigest()
    assert Sha256(input_str).hexdigest() == expected

def test_long_input():
    input_str = "a" * 99999
    expected = hashlib.sha256(input_str.encode()).hexdigest()
    assert Sha256(input_str).hexdigest() == expected

def test_digest_vs_hexdigest():
    input_str = "test"
    custom = Sha256(input_str)
    assert custom.hexdigest() == custom.digest().hex()
