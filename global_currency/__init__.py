"""Global Historical Currency Converter package."""

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
from global_currency.models import ConversionResult, CurrencyInfo, RateObservation

__version__ = "0.1.0"

__all__ = [
    "CurrencyConverter",
    "convert",
    "convert_value",
    "get_rate",
    "history",
    "currency_info",
    "list_currencies",
    "currency_for_country",
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
