"""Tests for currency metadata lookup and country mappings."""

import pytest
from datetime import date

from global_currency.countries import currency_for_country
from global_currency.currencies import currency_info, list_currencies
from global_currency.exceptions import UnsupportedCurrencyError


def test_currency_info_active():
    info = currency_info("USD")
    assert info.code == "USD"
    assert info.name == "United States Dollar"
    assert info.symbol == "$"
    assert info.active is True


def test_currency_info_legacy():
    info = currency_info("DEM")
    assert info.code == "DEM"
    assert info.name == "German Mark"
    assert info.active is False
    assert info.start_date == "1948-06-21"
    assert info.end_date == "2001-12-31"


def test_currency_info_invalid():
    with pytest.raises(UnsupportedCurrencyError):
        currency_info("XYZ123")


def test_list_currencies():
    all_currs = list_currencies(active_only=False)
    active_currs = list_currencies(active_only=True)

    assert len(all_currs) > len(active_currs)
    assert any(c.code == "DEM" for c in all_currs)
    assert not any(c.code == "DEM" for c in active_currs)


def test_currency_for_country_historical():
    # Germany in 1995 -> DEM
    dem = currency_for_country("Germany", date="1995-05-01")
    assert dem == "DEM"

    # Germany in 2026 -> EUR
    eur = currency_for_country("Germany", date="2026-01-01")
    assert eur == "EUR"


def test_currency_for_country_unknown():
    with pytest.raises(UnsupportedCurrencyError):
        currency_for_country("Atlantis")
