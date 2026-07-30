"""Tests for gap fallback strategies (strict, previous, next, nearest)."""

from datetime import date
from decimal import Decimal
import pytest

from global_currency.cache import SQLiteCache
from global_currency.exceptions import HistoricalRateNotFound
from global_currency.models import RateObservation
from global_currency.resolver import RateResolver


class DummyProvider:
    name = "Dummy"

    def supports(self, currency):
        return True

    def get_rate(self, base, quote, target_date, provider_pin=None):
        # Observation available on Friday 2005-03-18 and Monday 2005-03-21
        # No observation on Saturday 2005-03-19 or Sunday 2005-03-20
        if target_date == date(2005, 3, 18):
            return RateObservation(
                base=base,
                quote=quote,
                rate=Decimal("43.60"),
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
            )
        if target_date == date(2005, 3, 21):
            return RateObservation(
                base=base,
                quote=quote,
                rate=Decimal("43.70"),
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
            )
        return None


@pytest.fixture
def resolver(tmp_path):
    cache = SQLiteCache(db_path=tmp_path / "test.db")
    return RateResolver(providers=[DummyProvider()], cache=cache)


def test_gap_fallback_strict(resolver):
    # Sunday 2005-03-20 has no observation
    with pytest.raises(HistoricalRateNotFound):
        resolver.resolve_rate("USD", "INR", date(2005, 3, 20), fallback="strict")


def test_gap_fallback_previous(resolver):
    # Sunday 2005-03-20 -> fallback previous -> Friday 2005-03-18
    obs = resolver.resolve_rate("USD", "INR", date(2005, 3, 20), fallback="previous")
    assert obs.rate == Decimal("43.60")
    assert obs.requested_date == date(2005, 3, 20)
    assert obs.rate_date == date(2005, 3, 18)
    assert obs.fallback_used == "previous"


def test_gap_fallback_next(resolver):
    # Saturday 2005-03-19 -> fallback next -> Monday 2005-03-21
    obs = resolver.resolve_rate("USD", "INR", date(2005, 3, 19), fallback="next")
    assert obs.rate == Decimal("43.70")
    assert obs.requested_date == date(2005, 3, 19)
    assert obs.rate_date == date(2005, 3, 21)
    assert obs.fallback_used == "next"


def test_gap_fallback_nearest(resolver):
    # Saturday 2005-03-19: Friday is 1 day away, Monday is 2 days away -> Friday (previous)
    obs = resolver.resolve_rate("USD", "INR", date(2005, 3, 19), fallback="nearest")
    assert obs.rate_date == date(2005, 3, 18)
    assert obs.fallback_used == "previous"
