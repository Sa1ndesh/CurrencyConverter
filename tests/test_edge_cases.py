"""Edge case tests for financial Decimal precision, invalid inputs, and error handling."""

from datetime import date
from decimal import Decimal
import pytest

from global_currency.converter import CurrencyConverter, convert
from global_currency.exceptions import (
    CurrencyError,
    HistoricalRateNotFound,
    InvalidAmountError,
    InvalidDateError,
    UnsupportedCurrencyError,
)


def test_invalid_currency_code():
    with pytest.raises(UnsupportedCurrencyError):
        convert(100, "INVALID", "USD")

    with pytest.raises(UnsupportedCurrencyError):
        convert(100, "USD", "BADCODE")


def test_invalid_date_format():
    with pytest.raises(InvalidDateError):
        convert(100, "USD", "INR", date="03/18/2005")


def test_invalid_amount():
    with pytest.raises(InvalidAmountError):
        convert("not_a_number", "USD", "INR")


def test_decimal_precision():
    converter = CurrencyConverter()
    # Ensure float conversion string parsing keeps high precision
    res = converter.convert("123456789.987654321", "USD", "USD")
    assert res.result == Decimal("123456789.987654321")
