"""ExchangeRateHost exchange rate provider."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
import requests

from global_currency.models import RateObservation
from global_currency.providers.base import ExchangeRateProvider


class ExchangeRateHostProvider(ExchangeRateProvider):
    """Provider for ExchangeRate.host API rates."""

    name = "ExchangeRateHost"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://api.exchangerate.host"

    def supports(self, currency: str) -> bool:
        return True

    def get_rate(
        self,
        base: str,
        quote: str,
        target_date: date,
        provider_pin: Optional[str] = None
    ) -> Optional[RateObservation]:
        base_u = base.upper()
        quote_u = quote.upper()
        date_str = target_date.isoformat()

        url = f"{self.base_url}/{date_str}"
        params = {"base": base_u, "symbols": quote_u}
        if self.api_key:
            params["access_key"] = self.api_key

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success", True) and "rates" in data:
                    rate_val = data["rates"].get(quote_u)
                    if rate_val is not None:
                        return RateObservation(
                            base=base_u,
                            quote=quote_u,
                            rate=Decimal(str(rate_val)),
                            requested_date=target_date,
                            rate_date=target_date,
                            provider=self.name,
                            source_providers=(self.name,),
                            frequency="daily",
                        )
        except Exception:
            return None

        return None

    def get_series(
        self,
        base: str,
        quote: str,
        start_date: date,
        end_date: date
    ) -> List[RateObservation]:
        return []
