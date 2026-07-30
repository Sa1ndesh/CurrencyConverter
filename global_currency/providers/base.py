"""Abstract base provider class for exchange rate data sources."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from global_currency.models import RateObservation


class ExchangeRateProvider(ABC):
    """Abstract base class for all exchange rate data providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier name."""
        pass

    @abstractmethod
    def supports(self, currency: str) -> bool:
        """Check if provider supports the given 3-letter currency code."""
        pass

    @abstractmethod
    def get_rate(
        self,
        base: str,
        quote: str,
        target_date: date,
        provider_pin: Optional[str] = None
    ) -> Optional[RateObservation]:
        """Retrieve rate observation for base/quote pair on target_date.

        Should return None if no observation is available from this provider.
        """
        pass

    @abstractmethod
    def get_series(
        self,
        base: str,
        quote: str,
        start_date: date,
        end_date: date
    ) -> List[RateObservation]:
        """Retrieve historical series of observations for date range."""
        pass
