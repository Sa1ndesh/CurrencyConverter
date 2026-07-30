"""Tests for CurrencyConverter facade, convert(), convert_value(), and integration behavior."""

from datetime import date
from decimal import Decimal
import pytest

from global_currency.converter import CurrencyConverter, convert, convert_value
from global_currency.exceptions import HistoricalRateNotFound
from global_currency.models import ConversionResult, RateObservation


class MockProvider:
    name = "MockProvider"

    def supports(self, currency):
        return True

    def get_rate(self, base, quote, target_date, provider_pin=None):
        if base == "USD" and quote == "INR" and target_date == date(2005, 3, 18):
            return RateObservation(
                base="USD",
                quote="INR",
                rate=Decimal("43.602"),
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
                source_providers=("MockCB",),
                source_series="MOCK_USD_INR",
                frequency="daily",
            )
        if base == "USD" and quote == "JPY" and target_date == date(2005, 3, 18):
            return RateObservation(
                base="USD",
                quote="JPY",
                rate=Decimal("105.00"),
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
                source_series="MOCK_USD_JPY",
                frequency="daily",
            )
        return None


@pytest.fixture
def mock_converter(tmp_path):
    from global_currency.cache import SQLiteCache
    cache = SQLiteCache(db_path=tmp_path / "test.db")
    return CurrencyConverter(providers=[MockProvider()], cache=cache)


def test_converter_same_currency(mock_converter):
    res = mock_converter.convert(100, "USD", "USD", date_val="2005-03-18")
    assert res.result == Decimal("100")
    assert res.rate == Decimal("1")
    assert res.from_currency == "USD"
    assert res.to_currency == "USD"


def test_converter_direct_pair(mock_converter):
    res = mock_converter.convert(10, "USD", "INR", date_val="2005-03-18")
    assert isinstance(res, ConversionResult)
    assert res.result == Decimal("436.020")
    assert res.rate == Decimal("43.602")
    assert res.provider == "MockProvider"
    assert res.source_providers == ("MockCB",)
    assert res.frequency == "daily"
    assert res.derived is False


def test_converter_convert_value_shortcut(mock_converter):
    val = mock_converter.convert_value(10, "USD", "INR", date_val="2005-03-18")
    assert isinstance(val, Decimal)
    assert val == Decimal("436.020")


def test_cross_rate_derivation(mock_converter):
    # INR -> USD -> JPY cross conversion
    res = mock_converter.convert(1000, "INR", "JPY", date_val="2005-03-18")
    assert res.derived is True
    assert res.derivation_path == ("INR", "USD", "JPY")
    assert res.source_observations is not None
    assert len(res.source_observations) == 2


def test_integration_2005_usd_inr():
    """Integration test for USD/INR requested on 2005-03-18.

    Asserts either:
    A) A valid observation is returned with complete provenance metadata; OR
    B) HistoricalRateNotFound is raised cleanly if no provider has coverage.
    """
    converter = CurrencyConverter()  # Uses live Frankfurter, BIS, IMF providers
    try:
        res = converter.convert(1, "USD", "INR", date_val="2005-03-18", fallback="previous")
        assert res.amount == Decimal("1")
        assert res.from_currency == "USD"
        assert res.to_currency == "INR"
        assert isinstance(res.result, Decimal)
        assert res.result > 0
        assert res.requested_date == date(2005, 3, 18)
        assert isinstance(res.rate_date, date)
        assert res.provider is not None
        assert res.frequency in ("daily", "monthly", "quarterly", "annual")
    except HistoricalRateNotFound as e:
        # Valid behavior if offline or no dataset coverage found under gap strategy
        assert "2005-03-18" in str(e) or "USD/INR" in str(e)
