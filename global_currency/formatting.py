"""Currency formatting utilities."""

from decimal import Decimal
from typing import Union

from global_currency.currencies import currency_info


def format_currency(
    amount: Union[int, float, str, Decimal],
    currency_code: str,
    include_symbol: bool = True,
    decimals: int = 2
) -> str:
    """Format a monetary amount according to currency conventions.

    Args:
        amount: Number or Decimal value to format.
        currency_code: 3-letter ISO 4217 currency code (e.g., "USD", "INR", "EUR").
        include_symbol: Whether to prepend/append currency symbol (default: True).
        decimals: Number of decimal places (default: 2).

    Returns:
        Formatted currency string (e.g. "₹12,345.67", "$100.00").
    """
    code_upper = currency_code.strip().upper()
    try:
        info = currency_info(code_upper)
        symbol = info.symbol if info.symbol else code_upper
    except Exception:
        symbol = code_upper

    dec_val = Decimal(str(amount))
    formatted_num = f"{dec_val:,.{decimals}f}"

    if include_symbol:
        return f"{symbol}{formatted_num}"
    return f"{formatted_num} {code_upper}"
