"""BIS (Bank for International Settlements) SDMX exchange rate provider adapter."""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
import requests

from global_currency.exceptions import ProviderUnavailableError
from global_currency.models import RateObservation
from global_currency.providers.base import ExchangeRateProvider

logger = logging.getLogger(__name__)


class BISProvider(ExchangeRateProvider):
    """Provider adapter for Bank for International Settlements (BIS) bilateral exchange rate data."""

    BASE_URL = "https://stats.bis.org/api/v1/data"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "BIS"

    def supports(self, currency: str) -> bool:
        # BIS tracks major world currencies and economies
        return bool(currency and len(currency) == 3)

    def get_rate(
        self,
        base: str,
        quote: str,
        target_date: date,
        provider_pin: Optional[str] = None
    ) -> Optional[RateObservation]:
        base_u = base.upper()
        quote_u = quote.upper()

        # BIS bilateral series code key template: D.XRU.USD.<QUOTE>
        # Note: If base is not USD, resolver cross-rate handles pivot
        if base_u != "USD" and quote_u != "USD":
            return None

        target_curr = quote_u if base_u == "USD" else base_u
        date_str = target_date.isoformat()

        # BIS SDMX REST query format: BIS,WS_XRU,1.0/D.{target_curr}.USD
        url = f"{self.BASE_URL}/BIS,WS_XRU,1.0/D.{target_curr}.USD"
        params = {
            "startPeriod": date_str,
            "endPeriod": date_str,
            "format": "jsondata"
        }

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                return None
            data = resp.json()

            # Parse SDMX JSON response structure
            structure = data.get("dataSets", [{}])[0]
            series_data = structure.get("series", {})
            if not series_data:
                return None

            first_series_key = next(iter(series_data))
            obs_map = series_data[first_series_key].get("observations", {})
            if not obs_map:
                return None

            obs_val = next(iter(obs_map.values()))[0]
            rate_val = Decimal(str(obs_val))

            # Invert rate if base was not USD
            if base_u != "USD":
                rate_val = Decimal("1") / rate_val

            return RateObservation(
                base=base_u,
                quote=quote_u,
                rate=rate_val,
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
                source_providers=("BIS",),
                source_series=f"BIS_WS_XRU_D_{target_curr}_USD",
                frequency="daily",
                derived=False,
                derivation_path=None,
                source_observations=None,
                fallback_used=None,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"BIS SDMX API request failed: {e}")
            return None
        except (ValueError, KeyError, IndexError, DecimalException) as e:
            logger.warning(f"BIS SDMX response parsing error: {e}")
            return None

    def get_series(
        self,
        base: str,
        quote: str,
        start_date: date,
        end_date: date
    ) -> List[RateObservation]:
        return []
