"""Frankfurter API v2 exchange-rate provider adapter."""

from __future__ import annotations

import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, List, Optional, Tuple

import requests

from global_currency.exceptions import ProviderUnavailableError
from global_currency.models import RateObservation
from global_currency.providers.base import ExchangeRateProvider


logger = logging.getLogger(__name__)


class FrankfurterProvider(ExchangeRateProvider):
    """Exchange-rate provider using the Frankfurter v2 REST API."""

    BASE_URL = "https://api.frankfurter.dev/v2"

    def __init__(
        self,
        timeout: int = 10,
        base_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        self.timeout = timeout
        self.base_url = (base_url or self.BASE_URL).rstrip("/")
        self.session = session or requests.Session()

    @property
    def name(self) -> str:
        return "Frankfurter"

    def supports(self, currency: str) -> bool:
        """
        Perform basic ISO-code validation.

        This does not guarantee that Frankfurter actually has data for
        the currency. The API remains the authority for availability.
        """
        return (
            isinstance(currency, str)
            and len(currency.strip()) == 3
            and currency.strip().isalpha()
        )

    # ---------------------------------------------------------
    # HTTP
    # ---------------------------------------------------------

    def _fetch_url(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Fetch JSON data from Frankfurter."""

        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            response = self.session.get(
                url,
                params=params or {},
                timeout=self.timeout,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout as exc:
            logger.warning("Frankfurter request timed out: %s", exc)

            raise ProviderUnavailableError(
                "Frankfurter API request timed out."
            ) from exc

        except requests.exceptions.RequestException as exc:
            logger.warning("Frankfurter API request failed: %s", exc)

            raise ProviderUnavailableError(
                f"Frankfurter API query failed: {exc}"
            ) from exc

        except ValueError as exc:
            logger.warning("Frankfurter returned invalid JSON: %s", exc)

            raise ProviderUnavailableError(
                "Frankfurter returned an invalid JSON response."
            ) from exc

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _parse_date(value: Any, default: date) -> date:
        """Convert API date value into datetime.date."""

        if not value:
            return default

        try:
            return datetime.strptime(
                str(value),
                "%Y-%m-%d",
            ).date()

        except (TypeError, ValueError):
            logger.warning(
                "Invalid Frankfurter observation date %r; "
                "using requested date %s",
                value,
                default,
            )

            return default

    @staticmethod
    def _parse_rate(value: Any) -> Decimal:
        """Convert an API rate into Decimal without float arithmetic."""

        try:
            return Decimal(str(value))

        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ProviderUnavailableError(
                f"Frankfurter returned an invalid rate: {value!r}"
            ) from exc

    @staticmethod
    def _extract_source_providers(
        data: dict[str, Any],
        provider_pin: Optional[str] = None,
    ) -> Optional[Tuple[str, ...]]:
        """
        Extract provider attribution returned by expand=providers.

        Frankfurter v2 may return provider keys directly or provider
        objects depending on the response shape/version. Support both.
        """

        providers = data.get("providers")

        if not isinstance(providers, list):
            if provider_pin:
                return (provider_pin,)
            return None

        result: list[str] = []

        for provider in providers:

            # Example:
            # ["ECB", "BOE"]
            if isinstance(provider, str):
                if provider:
                    result.append(provider)
                continue

            # Defensive support for richer provider objects.
            if isinstance(provider, dict):

                if provider.get("excluded", False):
                    continue

                key = (
                    provider.get("key")
                    or provider.get("provider")
                    or provider.get("name")
                )

                if key:
                    result.append(str(key))

        if not result and provider_pin:
            result.append(provider_pin)

        if not result:
            return None

        # Remove duplicates while retaining order.
        return tuple(dict.fromkeys(result))

    # ---------------------------------------------------------
    # Single rate
    # ---------------------------------------------------------

    def get_rate(
        self,
        base: str,
        quote: str,
        target_date: date,
        provider_pin: Optional[str] = None,
    ) -> Optional[RateObservation]:
        """
        Retrieve one historical/current currency-pair observation.

        Example endpoint:

            /v2/rate/USD/INR?date=2005-03-18&expand=providers
        """

        base_u = base.strip().upper()
        quote_u = quote.strip().upper()

        if not self.supports(base_u):
            return None

        if not self.supports(quote_u):
            return None

        # Same-currency conversion does not require the provider.
        if base_u == quote_u:
            return RateObservation(
                base=base_u,
                quote=quote_u,
                rate=Decimal("1"),
                requested_date=target_date,
                rate_date=target_date,
                provider=self.name,
                source_providers=None,
                source_series=None,
                frequency="daily",
                derived=False,
                derivation_path=None,
                source_observations=None,
                fallback_used=None,
            )

        path = f"rate/{base_u}/{quote_u}"

        params: dict[str, str] = {
            "date": target_date.isoformat(),
            "expand": "providers",
        }

        # Frankfurter v2 uses "providers", not "provider".
        if provider_pin:
            params["providers"] = provider_pin

        data = self._fetch_url(path, params)

        if not isinstance(data, dict):
            return None

        if "rate" not in data:
            return None

        rate = self._parse_rate(data["rate"])

        observation_date = self._parse_date(
            data.get("date"),
            target_date,
        )

        source_providers = self._extract_source_providers(
            data,
            provider_pin,
        )

        return RateObservation(
            base=base_u,
            quote=quote_u,
            rate=rate,

            # The date requested by our user.
            requested_date=target_date,

            # Actual observation date reported by Frankfurter.
            rate_date=observation_date,

            # Frankfurter is the aggregator/API provider.
            provider=self.name,

            # Underlying provider attribution from expand=providers.
            source_providers=source_providers,

            # Frankfurter does not expose a BIS/IMF-style series ID
            # through this endpoint.
            source_series=None,

            # This describes an ungrouped Frankfurter v2 rate
            # observation. Do not infer an underlying central-bank
            # publication frequency from this field.
            frequency="daily",

            derived=False,
            derivation_path=None,
            source_observations=None,
            fallback_used=None,
        )

    # ---------------------------------------------------------
    # Time series
    # ---------------------------------------------------------

    def get_series(
        self,
        base: str,
        quote: str,
        start_date: date,
        end_date: date,
        provider_pin: Optional[str] = None,
    ) -> List[RateObservation]:
        """
        Retrieve a historical time series.

        Frankfurter v2 uses:

            /v2/rates
                ?base=USD
                &quotes=INR
                &from=2005-03-01
                &to=2005-03-31
                &expand=providers
        """

        base_u = base.strip().upper()
        quote_u = quote.strip().upper()

        if not self.supports(base_u):
            return []

        if not self.supports(quote_u):
            return []

        if start_date > end_date:
            return []

        path = "rates"

        params: dict[str, str] = {
            "base": base_u,
            "quotes": quote_u,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "expand": "providers",
        }

        if provider_pin:
            params["providers"] = provider_pin

        data = self._fetch_url(path, params)

        if not isinstance(data, list):
            return []

        observations: List[RateObservation] = []

        for item in data:

            if not isinstance(item, dict):
                continue

            item_base = str(
                item.get("base", base_u)
            ).upper()

            item_quote = str(
                item.get("quote", quote_u)
            ).upper()

            # Only retain the requested pair.
            if item_base != base_u:
                continue

            if item_quote != quote_u:
                continue

            if "rate" not in item:
                continue

            try:
                rate = self._parse_rate(item["rate"])
            except ProviderUnavailableError:
                logger.warning(
                    "Skipping malformed Frankfurter observation: %r",
                    item,
                )
                continue

            observation_date = self._parse_date(
                item.get("date"),
                start_date,
            )

            source_providers = self._extract_source_providers(
                item,
                provider_pin,
            )

            observation = RateObservation(
                base=base_u,
                quote=quote_u,
                rate=rate,

                # A series observation is itself associated with
                # its observation date.
                requested_date=observation_date,
                rate_date=observation_date,

                provider=self.name,
                source_providers=source_providers,
                source_series=None,
                frequency="daily",

                derived=False,
                derivation_path=None,
                source_observations=None,
                fallback_used=None,
            )

            observations.append(observation)

        observations.sort(
            key=lambda observation: observation.rate_date
        )

        return observations