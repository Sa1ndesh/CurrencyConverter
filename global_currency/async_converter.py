"""Asynchronous currency converter interface wrapping synchronous operations in thread executors."""

import asyncio
from datetime import date
from decimal import Decimal
from typing import List, Optional, Union

from global_currency.converter import CurrencyConverter
from global_currency.models import ConversionResult, RateObservation


class AsyncCurrencyConverter:
    """Async facade for CurrencyConverter providing asynchronous conversion methods."""

    def __init__(self, converter: Optional[CurrencyConverter] = None):
        self.converter = converter or CurrencyConverter()

    async def convert(
        self,
        amount: Union[int, float, str, Decimal],
        from_currency: str,
        to_currency: str,
        date_val: Optional[Union[str, date]] = None,
        date: Optional[Union[str, date]] = None,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> ConversionResult:
        """Asynchronously convert currency amount."""
        effective_d = date if date is not None else date_val
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.converter.convert(
                amount=amount,
                from_currency=from_currency,
                to_currency=to_currency,
                date=effective_d,
                fallback=fallback,
                provider_pin=provider_pin,
            )
        )

    async def convert_value(
        self,
        amount: Union[int, float, str, Decimal],
        from_currency: str,
        to_currency: str,
        date_val: Optional[Union[str, date]] = None,
        date: Optional[Union[str, date]] = None,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> Decimal:
        """Asynchronously convert currency amount and return Decimal value."""
        res = await self.convert(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            date_val=date_val,
            date=date,
            fallback=fallback,
            provider_pin=provider_pin,
        )
        return res.result

    async def get_rate(
        self,
        base: str,
        quote: str,
        date_val: Optional[Union[str, date]] = None,
        date: Optional[Union[str, date]] = None,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> RateObservation:
        """Asynchronously get exchange rate observation."""
        effective_d = date if date is not None else date_val
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.converter.get_rate(
                base=base,
                quote=quote,
                date=effective_d,
                fallback=fallback,
                provider_pin=provider_pin,
            )
        )

    async def history(
        self,
        base: str,
        quote: str,
        start_date: Union[str, date],
        end_date: Union[str, date]
    ) -> List[RateObservation]:
        """Asynchronously retrieve historical series."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.converter.history(
                base=base,
                quote=quote,
                start_date=start_date,
                end_date=end_date,
            )
        )
