"""Main CurrencyConverter facade, cross-rate calculation engine, and public API functions."""

from datetime import date, datetime
from decimal import Decimal, DecimalException
from typing import List, Optional, Union

from global_currency.cache import SQLiteCache
from global_currency.currencies import currency_info
from global_currency.exceptions import (
    CurrencyError,
    HistoricalRateNotFound,
    InvalidAmountError,
    InvalidDateError,
    UnsupportedCurrencyError,
)
from global_currency.models import ConversionResult, RateObservation
from global_currency.providers import (
    BISProvider,
    ExchangeRateProvider,
    FrankfurterProvider,
    IMFProvider,
)
from global_currency.resolver import RateResolver


def _parse_date(d: Optional[Union[str, date]]) -> date:
    if d is None:
        return date.today()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        try:
            return datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateError(f"Invalid date format '{d}'. Expected YYYY-MM-DD.")
    raise InvalidDateError("Date must be a string or datetime.date object.")


def _to_decimal(val: Union[int, float, str, Decimal]) -> Decimal:
    try:
        d = Decimal(str(val))
        if d.is_nan() or d.is_infinite():
            raise InvalidAmountError(f"Invalid amount '{val}'.")
        return d
    except (ValueError, TypeError, DecimalException):
        raise InvalidAmountError(f"Invalid monetary amount: {val}")


class CurrencyConverter:
    """High-level currency converter with multi-provider fallbacks, gap strategies, and cross-rate calculation."""

    def __init__(
        self,
        providers: Optional[List[ExchangeRateProvider]] = None,
        cache: Optional[SQLiteCache] = None,
        pivot_currency: str = "USD"
    ):
        if providers is None:
            # Default provider chain: Frankfurter, BIS, IMF
            providers = [
                FrankfurterProvider(),
                BISProvider(),
                IMFProvider(),
            ]
        self.cache = cache or SQLiteCache()
        self.resolver = RateResolver(providers=providers, cache=self.cache)
        self.pivot_currency = pivot_currency.upper()

    def get_rate(
        self,
        base: str,
        quote: str,
        date_val: Optional[Union[str, date]] = None,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> RateObservation:
        """Retrieve rate observation for base/quote pair on date_val.

        Args:
            base: 3-letter source currency code.
            quote: 3-letter target currency code.
            date_val: Target date (YYYY-MM-DD or date object). Defaults to today.
            fallback: Gap handling strategy ("previous", "next", "nearest", "strict").
            provider_pin: Optional provider name filter.

        Returns:
            RateObservation with full provenance.
        """
        # Validate currency codes
        info_base = currency_info(base)
        info_quote = currency_info(quote)
        target_d = _parse_date(date_val)

        # 1. Attempt direct pair resolution
        try:
            return self.resolver.resolve_rate(
                base=info_base.code,
                quote=info_quote.code,
                target_date=target_d,
                fallback=fallback,
                provider_pin=provider_pin,
            )
        except HistoricalRateNotFound:
            pass

        # 2. Attempt cross-rate derivation via pivot currency (e.g. USD or EUR)
        pivot = self.pivot_currency
        if info_base.code != pivot and info_quote.code != pivot:
            try:
                obs1 = self.resolver.resolve_rate(
                    base=pivot,
                    quote=info_base.code,
                    target_date=target_d,
                    fallback=fallback,
                    provider_pin=provider_pin,
                )
                obs2 = self.resolver.resolve_rate(
                    base=pivot,
                    quote=info_quote.code,
                    target_date=target_d,
                    fallback=fallback,
                    provider_pin=provider_pin,
                )

                # Cross-rate calculation: quote_rate / base_rate
                cross_rate = obs2.rate / obs1.rate

                # Determine effective market observation date
                effective_date = max(obs1.rate_date, obs2.rate_date)

                return RateObservation(
                    base=info_base.code,
                    quote=info_quote.code,
                    rate=cross_rate,
                    requested_date=target_d,
                    rate_date=effective_date,
                    provider=f"{obs1.provider}/{obs2.provider}",
                    source_providers=(obs1.provider, obs2.provider),
                    source_series=None,
                    frequency=obs1.frequency,
                    derived=True,
                    derivation_path=(info_base.code, pivot, info_quote.code),
                    source_observations=(obs1, obs2),
                    fallback_used=obs1.fallback_used or obs2.fallback_used,
                )
            except HistoricalRateNotFound:
                pass

        raise HistoricalRateNotFound(
            f"No exchange rate observation found for {info_base.code}/{info_quote.code} on {target_d}."
        )

    def convert(
        self,
        amount: Union[int, float, str, Decimal],
        from_currency: str,
        to_currency: str,
        date_val: Optional[Union[str, date]] = None,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> ConversionResult:
        """Convert currency amount returning complete ConversionResult with full auditability.

        Args:
            amount: Monetary value to convert.
            from_currency: Source currency ISO code.
            to_currency: Target currency ISO code.
            date_val: Requested date (YYYY-MM-DD or date object). Defaults to today.
            fallback: Gap handling strategy ("previous", "next", "nearest", "strict").
            provider_pin: Optional provider name filter.

        Returns:
            ConversionResult object containing calculated amount and provenance metadata.
        """
        dec_amount = _to_decimal(amount)
        rate_obs = self.get_rate(
            base=from_currency,
            quote=to_currency,
            date_val=date_val,
            fallback=fallback,
            provider_pin=provider_pin,
        )

        converted_val = dec_amount * rate_obs.rate

        return ConversionResult(
            amount=dec_amount,
            from_currency=rate_obs.base,
            to_currency=rate_obs.quote,
            result=converted_val,
            rate=rate_obs.rate,
            requested_date=rate_obs.requested_date,
            rate_date=rate_obs.rate_date,
            provider=rate_obs.provider,
            source_providers=rate_obs.source_providers,
            source_series=rate_obs.source_series,
            frequency=rate_obs.frequency,
            derived=rate_obs.derived,
            derivation_path=rate_obs.derivation_path,
            source_observations=rate_obs.source_observations,
            fallback_used=rate_obs.fallback_used,
        )

    def convert_value(
        self,
        amount: Union[int, float, str, Decimal],
        from_currency: str,
        to_currency: str,
        date_val: Optional[Union[str, date]] = None,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> Decimal:
        """Shortcut to return raw Decimal conversion result value."""
        res = self.convert(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            date_val=date_val,
            fallback=fallback,
            provider_pin=provider_pin,
        )
        return res.result

    def history(
        self,
        base: str,
        quote: str,
        start_date: Union[str, date],
        end_date: Union[str, date]
    ) -> List[RateObservation]:
        """Retrieve historical series of observations for date range."""
        info_base = currency_info(base)
        info_quote = currency_info(quote)
        sd = _parse_date(start_date)
        ed = _parse_date(end_date)

        for p in self.resolver.providers:
            if p.supports(info_base.code) and p.supports(info_quote.code):
                try:
                    series = p.get_series(info_base.code, info_quote.code, sd, ed)
                    if series:
                        return series
                except Exception:
                    pass
        return []


# Module-level convenience functions using default converter instance
_DEFAULT_CONVERTER = None


def _get_default_converter() -> CurrencyConverter:
    global _DEFAULT_CONVERTER
    if _DEFAULT_CONVERTER is None:
        _DEFAULT_CONVERTER = CurrencyConverter()
    return _DEFAULT_CONVERTER


def convert(
    amount: Union[int, float, str, Decimal],
    from_currency: str,
    to_currency: str,
    date: Optional[Union[str, date]] = None,
    fallback: str = "previous"
) -> ConversionResult:
    """Module-level shortcut for CurrencyConverter.convert()."""
    return _get_default_converter().convert(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
        date_val=date,
        fallback=fallback,
    )


def convert_value(
    amount: Union[int, float, str, Decimal],
    from_currency: str,
    to_currency: str,
    date: Optional[Union[str, date]] = None,
    fallback: str = "previous"
) -> Decimal:
    """Module-level shortcut for CurrencyConverter.convert_value()."""
    return _get_default_converter().convert_value(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency,
        date_val=date,
        fallback=fallback,
    )


def get_rate(
    base: str,
    quote: str,
    date: Optional[Union[str, date]] = None,
    fallback: str = "previous"
) -> RateObservation:
    """Module-level shortcut for CurrencyConverter.get_rate()."""
    return _get_default_converter().get_rate(
        base=base,
        quote=quote,
        date_val=date,
        fallback=fallback,
    )


def history(
    base: str,
    quote: str,
    start_date: Union[str, date],
    end_date: Union[str, date]
) -> List[RateObservation]:
    """Module-level shortcut for CurrencyConverter.history()."""
    return _get_default_converter().history(
        base=base,
        quote=quote,
        start_date=start_date,
        end_date=end_date,
    )
