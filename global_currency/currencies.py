"""Currency metadata lookup functions."""

import json
from pathlib import Path
from typing import List, Optional

from global_currency.exceptions import UnsupportedCurrencyError
from global_currency.models import CurrencyInfo

_CURRENCIES_FILE = Path(__file__).parent / "data" / "currencies.json"
_CURRENCY_CACHE = None


def _load_currencies():
    global _CURRENCY_CACHE
    if _CURRENCY_CACHE is None:
        with open(_CURRENCIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CURRENCY_CACHE = data.get("currencies", {})
    return _CURRENCY_CACHE


def currency_info(code: str) -> CurrencyInfo:
    """Retrieve metadata for a specific ISO currency code.

    Args:
        code: 3-letter ISO 4217 currency code.

    Returns:
        CurrencyInfo dataclass containing currency metadata.

    Raises:
        UnsupportedCurrencyError: If code is not recognized.
    """
    if not code or not isinstance(code, str):
        raise UnsupportedCurrencyError("Currency code must be a non-empty string.")

    code_upper = code.strip().upper()
    currencies = _load_currencies()

    if code_upper not in currencies:
        raise UnsupportedCurrencyError(f"Unsupported or unknown currency code: '{code}'")

    raw = currencies[code_upper]
    return CurrencyInfo(
        code=raw["code"],
        name=raw["name"],
        symbol=raw.get("symbol", ""),
        numeric_code=raw.get("numeric_code"),
        active=raw.get("active", True),
        start_date=raw.get("start_date"),
        end_date=raw.get("end_date"),
    )


def list_currencies(active_only: bool = False) -> List[CurrencyInfo]:
    """Retrieve list of all supported currencies.

    Args:
        active_only: If True, returns only currently circulating currencies.

    Returns:
        List of CurrencyInfo objects.
    """
    currencies = _load_currencies()
    result = []
    for code, raw in currencies.items():
        info = CurrencyInfo(
            code=raw["code"],
            name=raw["name"],
            symbol=raw.get("symbol", ""),
            numeric_code=raw.get("numeric_code"),
            active=raw.get("active", True),
            start_date=raw.get("start_date"),
            end_date=raw.get("end_date"),
        )
        if active_only and not info.active:
            continue
        result.append(info)
    return result
