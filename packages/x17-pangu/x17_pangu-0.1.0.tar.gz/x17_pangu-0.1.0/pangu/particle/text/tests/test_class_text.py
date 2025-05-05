import hashlib
import pytest
from pangu.particle.text import Text


def test_text_creation_and_str_behavior():
    t = Text("sample")
    assert isinstance(t, str)
    assert str(t) == "sample"
    assert len(t) == 6
    assert t == "sample"
    assert t != "other"


def test_text_dict_property():
    t = Text("hello")
    assert t.dict == {"content": "hello"}


def test_text_upper_and_lower_properties():
    t = Text("HeLLo")
    assert t.upper == "HELLO"
    assert t.lower == "hello"


def test_text_repr_short_and_long():
    short = Text("short")
    long = Text("thisisaverylongtext")
    assert repr(short) == "Text(content=short)"
    assert repr(long) == "Text(content=thisisaver...)"


@pytest.mark.parametrize("algo", ["md5", "sha256", "sha512"])
def test_text_as_digest_valid_algorithms(algo):
    t = Text("digest-me")
    expected = hashlib.new(algo, b"digest-me").hexdigest()
    assert t.as_digest(algo) == expected


def test_text_as_digest_invalid_algorithm():
    t = Text("invalid")
    with pytest.raises(KeyError):
        t.as_digest("nonexistent_algo")


def test_text_wildcard_match_positive():
    t = Text("file_001.csv")
    assert t.wildcard_match("file_*.csv")
    assert t.wildcard_match("*.csv")
    assert t.wildcard_match("file_*")


def test_text_wildcard_match_negative():
    t = Text("file_001.csv")
    assert not t.wildcard_match("log_*.csv")
    assert not t.wildcard_match("*.txt")


def test_text_export_returns_expected_dict():
    t = Text("data")
    assert t.export() == {"content": "data"}


def test_text_export_with_empty_content():
    t = Text("")
    assert t.export() == {}
    
def test_to_snake():
    assert Text("CamelCaseText").to_snake() == "camel_case_text"
    assert Text("camelCaseText").to_snake() == "camel_case_text"
    assert Text("already_snake_case").to_snake() == "already_snake_case"

def test_to_camel():
    assert Text("snake_case_text").to_camel() == "snakeCaseText"
    assert Text("alreadyCamel").to_camel() == "alreadyCamel"

def between_snake_and_camel():
    sample_text = Text("sample_text")
    assert sample_text == "sample_text"
    sample_text = sample_text.to_camel()
    assert sample_text == "sampleText"
    sample_text = sample_text.to_snake()
    assert sample_text == "sample_text"
    sample_text = sample_text.to_camel()
    assert sample_text == "sampleText"
    sample_text = sample_text.to_snake()
    assert sample_text == "sample_text"

def test_snake_property():
    assert Text("SomeLongText").snake == "some_long_text"

def test_camel_property():
    assert Text("some_long_text").camel == "someLongText"

def test_len_override():
    assert len(Text("abcde")) == 5

def test_eq_and_ne():
    assert Text("abc") == "abc"
    assert Text("abc") == Text("abc")
    assert Text("abc") != "def"
    assert Text("abc") != Text("def")

def test_comparison_operators():
    assert Text("abc") < "bcd"
    assert Text("abc") <= "abc"
    assert Text("abc") > "abb"
    assert Text("abc") >= "abc"

def test_contains_operator():
    assert "bc" in Text("abcde")
    assert Text("cde") in Text("abcde")

def test_add_and_radd():
    assert Text("abc") + "def" == "abcdef"
    assert "def" + Text("abc") == "defabc"
    assert Text("abc") + Text("123") == "abc123"

def test_mul_and_rmul():
    assert Text("abc") * 3 == "abcabcabc"
    assert 2 * Text("xy") == "xyxy"