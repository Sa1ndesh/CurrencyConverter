"""Global Historical Currency Converter package."""

from global_currency.async_converter import AsyncCurrencyConverter
from global_currency.cache import MemoryCache, SQLiteCache
from global_currency.converter import (
    CurrencyConverter,
    convert,
    convert_value,
    get_rate,
    history,
)
from global_currency.countries import currency_for_country
from global_currency.currencies import currency_info, list_currencies
from global_currency.exceptions import (
    CurrencyError,
    HistoricalRateNotFound,
    InvalidAmountError,
    InvalidDateError,
    ProviderUnavailableError,
    UnsupportedCurrencyError,
)
from global_currency.formatting import format_currency
from global_currency.models import ConversionResult, CurrencyInfo, RateObservation

__version__ = "1.0.0"

__all__ = [
    "CurrencyConverter",
    "AsyncCurrencyConverter",
    "convert",
    "convert_value",
    "get_rate",
    "history",
    "currency_info",
    "list_currencies",
    "currency_for_country",
    "format_currency",
    "MemoryCache",
    "SQLiteCache",
    "RateObservation",
    "ConversionResult",
    "CurrencyInfo",
    "CurrencyError",
    "UnsupportedCurrencyError",
    "HistoricalRateNotFound",
    "InvalidDateError",
    "ProviderUnavailableError",
    "InvalidAmountError",
]

