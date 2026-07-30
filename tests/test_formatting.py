"""Tests for format_currency function."""

from decimal import Decimal
from global_currency import format_currency


def test_format_currency_inr():
    res = format_currency(12345.67, "INR")
    assert res == "₹12,345.67"


def test_format_currency_usd():
    res = format_currency("100.5", "USD")
    assert res == "$100.50"


def test_format_currency_without_symbol():
    res = format_currency(1000, "EUR", include_symbol=False)
    assert res == "1,000.00 EUR"
