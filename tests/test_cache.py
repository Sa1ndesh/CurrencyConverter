"""Tests for SQLite cache storing exact Decimal rates as TEXT."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import tempfile
import pytest

from global_currency.cache import SQLiteCache
from global_currency.models import RateObservation


@pytest.fixture
def temp_cache():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_cache.db"
        cache = SQLiteCache(db_path=db_path)
        yield cache


def test_sqlite_cache_save_and_get(temp_cache):
    obs = RateObservation(
        base="USD",
        quote="INR",
        rate=Decimal("43.60200000"),
        requested_date=date(2005, 3, 18),
        rate_date=date(2005, 3, 18),
        provider="Frankfurter",
        source_providers=("ECB",),
        source_series="FRANKFURTER_USD_INR",
        frequency="daily",
    )

    temp_cache.save_observation(obs)

    cached = temp_cache.get_rate("USD", "INR", date(2005, 3, 18))
    assert cached is not None
    assert cached.base == "USD"
    assert cached.quote == "INR"
    assert cached.rate == Decimal("43.60200000")  # Exact Decimal precision match
    assert isinstance(cached.rate, Decimal)
    assert cached.provider == "Frankfurter"
    assert cached.source_providers == ("ECB",)


def test_cache_miss(temp_cache):
    cached = temp_cache.get_rate("USD", "JPY", date(2000, 1, 1))
    assert cached is None
