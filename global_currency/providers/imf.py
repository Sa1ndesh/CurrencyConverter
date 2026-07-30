"""IMF (International Monetary Fund) SDMX exchange rate provider adapter."""

import logging
from datetime import date
from decimal import Decimal
from typing import List, Optional
import requests

from global_currency.exceptions import ProviderUnavailableError
from global_currency.models import RateObservation
from global_currency.providers.base import ExchangeRateProvider

logger = logging.getLogger(__name__)


class IMFProvider(ExchangeRateProvider):
    """Provider adapter for IMF (International Monetary Fund) SDMX exchange rate dataset."""

    BASE_URL = "https://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/ER"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "IMF"

    def supports(self, currency: str) -> bool:
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
        date_str = target_date.isoformat()

        # Target IMF series: e.g. D.IN.USD (Daily, National currency per USD)
        target_curr = quote_u if base_u == "USD" else base_u

        url = f"{self.BASE_URL}/D.{target_curr}.USD"
        params = {
            "startPeriod": date_str,
            "endPeriod": date_str
        }

        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
            if resp.status_code != 200:
                return None
            data = resp.json()

            compact_data = data.get("CompactData", {})
            dataset = compact_data.get("DataSet", {})
            series = dataset.get("Series")
            if not series:
                return None

            obs = series.get("Obs")
            if not obs:
                return None

            # Handle single observation vs list
            if isinstance(obs, dict):
                rate_str = obs.get("@OBS_VALUE")
            elif isinstance(obs, list) and len(obs) > 0:
                rate_str = obs[0].get("@OBS_VALUE")
            else:
                return None

            if not rate_str:
                return None

            rate_val = Decimal(str(rate_str))
            if base_u != "USD":
                rate_val = Decimal("1") / rate_val

            return RateObservation(
                base=base_u,
                quote=quote_u,
                rate=rate_val,
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
                source_providers=("IMF",),
                source_series=f"IMF_ER_D_{target_curr}_USD",
                frequency="daily",
                derived=False,
                derivation_path=None,
                source_observations=None,
                fallback_used=None,
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"IMF SDMX request failed: {e}")
            return None
        except Exception as e:
            logger.warning(f"IMF SDMX parse error: {e}")
            return None

    def get_series(
        self,
        base: str,
        quote: str,
        start_date: date,
        end_date: date
    ) -> List[RateObservation]:
        return []
