"""Country to currency mapping module supporting historical validity periods."""

import json
from datetime import date as date_type, datetime
from pathlib import Path
from typing import Optional, Union

from global_currency.exceptions import InvalidDateError, UnsupportedCurrencyError

_COUNTRIES_FILE = Path(__file__).parent / "data" / "countries.json"
_COUNTRIES_CACHE = None


def _load_countries():
    global _COUNTRIES_CACHE
    if _COUNTRIES_CACHE is None:
        with open(_COUNTRIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _COUNTRIES_CACHE = data.get("mappings", [])
    return _COUNTRIES_CACHE


def _parse_date(d: Optional[Union[str, date_type]]) -> Optional[date_type]:
    if d is None:
        return None
    if isinstance(d, date_type):
        return d
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateError(f"Invalid date format '{d}'. Expected YYYY-MM-DD.")
    raise InvalidDateError("Date must be a string or datetime.date instance.")


def currency_for_country(
    country_name: str,
    date: Optional[Union[str, date_type]] = None
) -> str:
    """Find active currency for a country on a specific date (or current date if omitted).

    Args:
        country_name: Name of the country (case-insensitive).
        date: Optional date string (YYYY-MM-DD) or date object.

    Returns:
        3-letter ISO currency code string.

    Raises:
        UnsupportedCurrencyError: If country is unknown or no currency active on date.
    """
    if not country_name or not isinstance(country_name, str):
        raise UnsupportedCurrencyError("Country name must be a non-empty string.")

    target_date = _parse_date(date) if date else date_type.today()
    country_clean = country_name.strip().lower()
    mappings = _load_countries()

    matched_country = False
    for item in mappings:
        if item["country"].lower() == country_clean:
            matched_country = True
            vf = _parse_date(item.get("valid_from"))
            vt = _parse_date(item.get("valid_to"))

            # Check date range boundary
            if vf and target_date < vf:
                continue
            if vt and target_date > vt:
                continue

            return item["currency_code"]

    if matched_country:
        raise UnsupportedCurrencyError(
            f"No active currency found for country '{country_name}' on date {target_date}."
        )

    raise UnsupportedCurrencyError(f"Unknown country '{country_name}'.")
