"""Tests for AsyncCurrencyConverter."""

import pytest
from decimal import Decimal
from datetime import date

from global_currency import AsyncCurrencyConverter, CurrencyConverter
from global_currency.models import RateObservation


class MockAsyncProvider:
    name = "MockAsyncProvider"

    def supports(self, currency):
        return True

    def get_rate(self, base, quote, target_date, provider_pin=None):
        if base == "USD" and quote == "EUR":
            return RateObservation(
                base="USD",
                quote="EUR",
                rate=Decimal("0.92"),
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
            )
        return None


@pytest.mark.asyncio
async def test_async_convert(tmp_path):
    from global_currency.cache import SQLiteCache
    cache = SQLiteCache(db_path=tmp_path / "test_async.db")
    sync_conv = CurrencyConverter(providers=[MockAsyncProvider()], cache=cache)
    async_conv = AsyncCurrencyConverter(converter=sync_conv)

    res = await async_conv.convert(100, "USD", "EUR", date="2024-01-01")
    assert res.result == Decimal("92.00")
    assert res.from_currency == "USD"
    assert res.to_currency == "EUR"

    val = await async_conv.convert_value(100, "USD", "EUR", date="2024-01-01")
    assert val == Decimal("92.00")

    rate_obs = await async_conv.get_rate("USD", "EUR", date="2024-01-01")
    assert rate_obs.rate == Decimal("0.92")
