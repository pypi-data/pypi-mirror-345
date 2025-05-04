import hashlib
from sha256py.core import Sha256

def test_known_hash():
    input_str = "hello"
    expected = hashlib.sha256(input_str.encode()).hexdigest()
    assert Sha256(input_str).hexdigest() == expected

def test_empty_string():
    expected = hashlib.sha256(b"").hexdigest()
    assert Sha256("").hexdigest() == expected

def test_long_input():
    input_str = "a" * 99999
    expected = hashlib.sha256(input_str.encode()).hexdigest()
    assert Sha256(input_str).hexdigest() == expected

def test_digest_vs_hexdigest():
    input_str = "test123"
    hasher = Sha256(input_str)
    assert hasher.hexdigest() == hasher.digest().hex()

def test_bindigest_matches_binary_string():
    input_str = "test123"
    custom = Sha256(input_str)
    bin_digest = custom.bindigest()

    expected = hashlib.sha256(input_str.encode()).digest()
    expected_bin = ''.join(f"{byte:08b}" for byte in expected)

    assert bin_digest == expected_bin

def test_unicode_input():
    input_str = "🐧⁜"
    expected = hashlib.sha256(input_str.encode()).hexdigest()
    assert Sha256(input_str).hexdigest() == expected
