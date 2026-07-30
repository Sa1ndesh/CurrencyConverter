"""RateResolver engine implementing multi-provider candidate collection, ranking, and gap strategies."""

import logging
from datetime import date, timedelta
from typing import List, Optional, Sequence

from global_currency.cache import SQLiteCache
from global_currency.exceptions import HistoricalRateNotFound
from global_currency.models import RateObservation
from global_currency.providers.base import ExchangeRateProvider

logger = logging.getLogger(__name__)


class RateResolver:
    """Collects candidate rate observations from cache and providers, ranking them strictly without fabricating rates."""

    def __init__(
        self,
        providers: Sequence[ExchangeRateProvider],
        cache: Optional[SQLiteCache] = None,
        max_lookback_days: int = 14
    ):
        self.providers = list(providers)
        self.cache = cache or SQLiteCache()
        self.max_lookback_days = max_lookback_days

    def resolve_rate(
        self,
        base: str,
        quote: str,
        target_date: date,
        fallback: str = "previous",
        provider_pin: Optional[str] = None
    ) -> RateObservation:
        """Resolve exchange rate for base/quote on target_date using fallback gap strategy.

        Args:
            base: Base currency code (e.g., "USD").
            quote: Quote currency code (e.g., "INR").
            target_date: Requested date.
            fallback: Gap handling strategy: "strict", "previous", "next", "nearest".
            provider_pin: Optional provider name filter.

        Returns:
            Winning RateObservation object with full provenance.

        Raises:
            HistoricalRateNotFound: If no observation can be resolved under the policy.
        """
        base_u = base.upper()
        quote_u = quote.upper()

        if base_u == quote_u:
            from decimal import Decimal
            return RateObservation(
                base=base_u,
                quote=quote_u,
                rate=Decimal("1"),
                requested_date=target_date,
                rate_date=target_date,
                provider="Identity",
                source_providers=("System",),
                source_series="IDENTITY",
                frequency="daily",
                derived=False,
            )

        # 1. Attempt exact date resolution
        exact_obs = self._gather_best_observation_for_date(base_u, quote_u, target_date, provider_pin)
        if exact_obs:
            return exact_obs

        # If fallback is strict, do not search adjacent dates
        if fallback == "strict":
            raise HistoricalRateNotFound(
                f"No exact exchange rate observation found for {base_u}/{quote_u} on {target_date} (fallback='strict')."
            )

        # 2. Execute Gap Substitution Strategies (previous, next, nearest)
        if fallback in ("previous", "nearest"):
            prev_obs = self._find_adjacent_observation(base_u, quote_u, target_date, direction="previous", provider_pin=provider_pin)
        else:
            prev_obs = None

        if fallback in ("next", "nearest"):
            next_obs = self._find_adjacent_observation(base_u, quote_u, target_date, direction="next", provider_pin=provider_pin)
        else:
            next_obs = None

        winning_obs: Optional[RateObservation] = None
        fallback_tag: Optional[str] = None

        if fallback == "previous":
            if prev_obs:
                winning_obs = prev_obs
                fallback_tag = "previous"
        elif fallback == "next":
            if next_obs:
                winning_obs = next_obs
                fallback_tag = "next"
        elif fallback == "nearest":
            if prev_obs and next_obs:
                delta_prev = abs((target_date - prev_obs.rate_date).days)
                delta_next = abs((next_obs.rate_date - target_date).days)
                if delta_prev <= delta_next:  # Tie goes to previous
                    winning_obs = prev_obs
                    fallback_tag = "previous"
                else:
                    winning_obs = next_obs
                    fallback_tag = "next"
            elif prev_obs:
                winning_obs = prev_obs
                fallback_tag = "previous"
            elif next_obs:
                winning_obs = next_obs
                fallback_tag = "next"

        if winning_obs:
            # Construct result preserving requested date & fallback tag
            res = RateObservation(
                base=winning_obs.base,
                quote=winning_obs.quote,
                rate=winning_obs.rate,
                requested_date=target_date,
                rate_date=winning_obs.rate_date,
                provider=winning_obs.provider,
                source_providers=winning_obs.source_providers,
                source_series=winning_obs.source_series,
                frequency=winning_obs.frequency,
                derived=winning_obs.derived,
                derivation_path=winning_obs.derivation_path,
                source_observations=winning_obs.source_observations,
                fallback_used=fallback_tag,
                fetched_at=winning_obs.fetched_at,
            )
            return res

        raise HistoricalRateNotFound(
            f"No exchange rate observation found for {base_u}/{quote_u} on {target_date} under gap strategy '{fallback}'."
        )

    def _gather_best_observation_for_date(
        self,
        base: str,
        quote: str,
        query_date: date,
        provider_pin: Optional[str] = None
    ) -> Optional[RateObservation]:
        candidates: List[RateObservation] = []

        # A. Check Local Cache
        cached = self.cache.get_rate(base, quote, query_date, provider=provider_pin)
        if cached:
            candidates.append(cached)

        # B. Check Configured Providers
        for p in self.providers:
            if provider_pin and p.name.lower() != provider_pin.lower():
                continue
            if p.supports(base) and p.supports(quote):
                try:
                    obs = p.get_rate(base, quote, query_date, provider_pin=provider_pin)
                    if obs:
                        # Cache fetched observation
                        self.cache.save_observation(obs)
                        candidates.append(obs)
                except Exception as e:
                    logger.warning(f"Provider '{p.name}' query failed for {base}/{quote} on {query_date}: {e}")

        if not candidates:
            return None

        # Rank candidates: 1. Exact date, 2. Direct over derived, 3. Provider priority order
        def rank_key(cand: RateObservation):
            exact = 0 if cand.rate_date == query_date else 1
            direct = 0 if not cand.derived else 1

            provider_idx = len(self.providers)
            for idx, p in enumerate(self.providers):
                if p.name.lower() == cand.provider.lower():
                    provider_idx = idx
                    break

            return (exact, direct, provider_idx)

        candidates.sort(key=rank_key)
        return candidates[0]

    def _find_adjacent_observation(
        self,
        base: str,
        quote: str,
        start_date: date,
        direction: str,  # "previous" or "next"
        provider_pin: Optional[str] = None
    ) -> Optional[RateObservation]:
        step = -1 if direction == "previous" else 1

        for day_offset in range(1, self.max_lookback_days + 1):
            curr_date = start_date + timedelta(days=step * day_offset)
            obs = self._gather_best_observation_for_date(base, quote, curr_date, provider_pin=provider_pin)
            if obs:
                return obs
        return None
