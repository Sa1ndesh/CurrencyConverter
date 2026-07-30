"""European Central Bank (ECB) exchange rate provider."""

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List, Optional
import xml.etree.ElementTree as ET
import requests

from global_currency.models import RateObservation
from global_currency.providers.base import ExchangeRateProvider


class ECBProvider(ExchangeRateProvider):
    """Provider for European Central Bank (ECB) official daily euro reference rates."""

    name = "ECB"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self._url_90_days = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml"

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
        if base_u != "EUR" and quote_u != "EUR":
            return None  # ECB uses EUR as base currency

        try:
            resp = requests.get(self._url_90_days, timeout=self.timeout)
            if resp.status_code != 200:
                return None

            tree = ET.fromstring(resp.content)
            # Namespace for ECB XML
            ns = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01', 'ecb': 'http://www.ecb.europa.eu/vocabulary/2002-08-01/eurofxref'}

            target_str = target_date.isoformat()
            for cube_time in tree.findall('.//ecb:Cube[@time]', ns):
                if cube_time.attrib.get('time') == target_str:
                    rates = {}
                    for cube_rate in cube_time.findall('ecb:Cube', ns):
                        curr = cube_rate.attrib.get('currency')
                        rate_val = cube_rate.attrib.get('rate')
                        if curr and rate_val:
                            rates[curr] = Decimal(rate_val)

                    rates['EUR'] = Decimal('1')

                    if base_u in rates and quote_u in rates:
                        final_rate = rates[quote_u] / rates[base_u]
                        return RateObservation(
                            base=base_u,
                            quote=quote_u,
                            rate=final_rate,
                            requested_date=target_date,
                            rate_date=target_date,
                            provider=self.name,
                            source_providers=("ECB",),
                            source_series="ECB_EUROFXREF",
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
