"""Data models for rate observations, conversion results, and currency metadata."""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Tuple


@dataclass(frozen=True)
class RateObservation:
    """Represents an immutable exchange rate observation from a data source."""

    base: str
    quote: str
    rate: Decimal
    requested_date: date
    rate_date: date  # Actual market observation date
    provider: str  # e.g., "Frankfurter", "BIS", "IMF"
    source_providers: Optional[Tuple[str, ...]] = None  # e.g., ("ECB", "BOE")
    source_series: Optional[str] = None  # e.g., "BIS_XRU_USD_INR"
    frequency: str = "daily"  # "daily", "monthly", "quarterly", "annual"
    derived: bool = False
    derivation_path: Optional[Tuple[str, ...]] = None  # e.g., ("INR", "USD", "JPY")
    source_observations: Optional[Tuple["RateObservation", ...]] = None  # Child observations for cross-rates
    fallback_used: Optional[str] = None  # "previous", "next", "nearest", None
    fetched_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert rate observation to a serializable dictionary."""
        return {
            "base": self.base,
            "quote": self.quote,
            "rate": str(self.rate),
            "requested_date": self.requested_date.isoformat(),
            "rate_date": self.rate_date.isoformat(),
            "provider": self.provider,
            "source_providers": list(self.source_providers) if self.source_providers else None,
            "source_series": self.source_series,
            "frequency": self.frequency,
            "derived": self.derived,
            "derivation_path": list(self.derivation_path) if self.derivation_path else None,
            "fallback_used": self.fallback_used,
            "fetched_at": self.fetched_at.isoformat(),
        }


@dataclass(frozen=True)
class ConversionResult:
    """Represents the complete result of a currency conversion with full provenance."""

    amount: Decimal
    from_currency: str
    to_currency: str
    result: Decimal
    rate: Decimal
    requested_date: date
    rate_date: date
    provider: str
    source_providers: Optional[Tuple[str, ...]] = None
    source_series: Optional[str] = None
    frequency: str = "daily"
    derived: bool = False
    derivation_path: Optional[Tuple[str, ...]] = None
    source_observations: Optional[Tuple[RateObservation, ...]] = None
    fallback_used: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert conversion result to a serializable dictionary."""
        return {
            "amount": str(self.amount),
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "result": str(self.result),
            "rate": str(self.rate),
            "requested_date": self.requested_date.isoformat(),
            "rate_date": self.rate_date.isoformat(),
            "provider": self.provider,
            "source_providers": list(self.source_providers) if self.source_providers else None,
            "source_series": self.source_series,
            "frequency": self.frequency,
            "derived": self.derived,
            "derivation_path": list(self.derivation_path) if self.derivation_path else None,
            "fallback_used": self.fallback_used,
        }


@dataclass(frozen=True)
class CurrencyInfo:
    """Metadata for an active or legacy currency."""

    code: str
    name: str
    symbol: str
    numeric_code: Optional[str] = None
    active: bool = True
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass(frozen=True)
class CountryCurrencyMap:
    """Historical mapping of a country to a currency over a date validity range."""

    country: str
    currency_code: str
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
