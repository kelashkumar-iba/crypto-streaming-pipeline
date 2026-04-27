"""Tests for producer module."""

from unittest.mock import MagicMock, patch

from producer.producer import build_message, fetch_prices


def test_build_message_complete_data():
    """Build message with all fields present."""
    coin = "bitcoin"
    values = {
        "usd": 78000,
        "usd_24h_change": 1.23,
        "last_updated_at": 1777200000,
    }
    msg = build_message(coin, values)
    assert msg == {
        "coin": "bitcoin",
        "price_usd": 78000,
        "change_24h": 1.23,
        "last_updated": 1777200000,
    }


def test_build_message_missing_fields():
    """Missing API fields default to None, not crash."""
    msg = build_message("ethereum", {"usd": 2300})
    assert msg["coin"] == "ethereum"
    assert msg["price_usd"] == 2300
    assert msg["change_24h"] is None
    assert msg["last_updated"] is None


def test_build_message_empty_values():
    """Completely empty values dict produces all-None message."""
    msg = build_message("dogecoin", {})
    assert msg["coin"] == "dogecoin"
    assert msg["price_usd"] is None
    assert msg["change_24h"] is None
    assert msg["last_updated"] is None


@patch("producer.producer.requests.get")
def test_fetch_prices_calls_correct_url(mock_get):
    """fetch_prices hits CoinGecko's simple/price endpoint with right params."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"bitcoin": {"usd": 78000}}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = fetch_prices()

    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "simple/price" in call_args[0][0]
    assert call_args[1]["params"]["vs_currencies"] == "usd"
    assert "bitcoin" in call_args[1]["params"]["ids"]
    assert result == {"bitcoin": {"usd": 78000}}
