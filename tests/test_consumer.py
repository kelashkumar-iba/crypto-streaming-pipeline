"""Tests for consumer module."""

from consumer.consumer import safe_deserializer


def test_safe_deserializer_valid_json():
    """Valid JSON bytes deserialize to dict."""
    raw = b'{"coin": "bitcoin", "price_usd": 78000}'
    result = safe_deserializer(raw)
    assert result == {"coin": "bitcoin", "price_usd": 78000}


def test_safe_deserializer_invalid_json_returns_none():
    """Malformed JSON returns None instead of crashing."""
    raw = b"not valid json {{{"
    result = safe_deserializer(raw)
    assert result is None


def test_safe_deserializer_invalid_utf8_returns_none():
    """Non-UTF8 bytes return None instead of crashing."""
    raw = b"\xff\xfe\xfd invalid utf8"
    result = safe_deserializer(raw)
    assert result is None


def test_safe_deserializer_empty_bytes_returns_none():
    """Empty bytes return None."""
    raw = b""
    result = safe_deserializer(raw)
    assert result is None
