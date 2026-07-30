"""SQLite local cache module storing exact Decimal rates as TEXT."""

import json
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import List, Optional, Tuple

from global_currency.models import RateObservation

_DEFAULT_CACHE_DIR = Path.home() / ".global_currency"
_DEFAULT_DB_PATH = _DEFAULT_CACHE_DIR / "rates_cache.db"


class SQLiteCache:
    """Persistent SQLite cache using TEXT storage for exact Decimal rates."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or _DEFAULT_DB_PATH
        if self.db_path != Path(":memory:"):
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS exchange_rates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        base_currency TEXT NOT NULL,
                        quote_currency TEXT NOT NULL,
                        observation_date TEXT NOT NULL,
                        rate TEXT NOT NULL,
                        provider TEXT NOT NULL,
                        source_providers TEXT,
                        source_series TEXT,
                        frequency TEXT NOT NULL,
                        derived INTEGER NOT NULL DEFAULT 0,
                        derivation_path TEXT,
                        fetched_at TEXT NOT NULL,

                        UNIQUE (
                            base_currency,
                            quote_currency,
                            observation_date,
                            provider,
                            source_series,
                            frequency
                        )
                    );
                    """
                )
        finally:
            conn.close()

    def get_rate(
        self,
        base: str,
        quote: str,
        observation_date: date,
        provider: Optional[str] = None,
        source_series: Optional[str] = None
    ) -> Optional[RateObservation]:
        """Fetch exact cached rate observation matching base, quote, date, and optional provider."""
        sql = """
            SELECT * FROM exchange_rates
            WHERE base_currency = ?
              AND quote_currency = ?
              AND observation_date = ?
        """
        params = [base.upper(), quote.upper(), observation_date.isoformat()]

        if provider:
            sql += " AND provider = ?"
            params.append(provider)
        if source_series:
            sql += " AND source_series = ?"
            params.append(source_series)

        sql += " ORDER BY fetched_at DESC LIMIT 1"

        conn = self._get_connection()
        try:
            row = conn.execute(sql, params).fetchone()
            if not row:
                return None
            return self._row_to_observation(row, observation_date)
        finally:
            conn.close()

    def search_candidates(
        self,
        base: str,
        quote: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider: Optional[str] = None
    ) -> List[RateObservation]:
        """Search range of candidate observations in SQLite cache."""
        sql = """
            SELECT * FROM exchange_rates
            WHERE base_currency = ? AND quote_currency = ?
        """
        params: list = [base.upper(), quote.upper()]

        if start_date:
            sql += " AND observation_date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            sql += " AND observation_date <= ?"
            params.append(end_date.isoformat())
        if provider:
            sql += " AND provider = ?"
            params.append(provider)

        sql += " ORDER BY observation_date DESC"

        conn = self._get_connection()
        try:
            rows = conn.execute(sql, params).fetchall()
            results = []
            for row in rows:
                obs_date = datetime.strptime(row["observation_date"], "%Y-%m-%d").date()
                results.append(self._row_to_observation(row, obs_date))
            return results
        finally:
            conn.close()

    def save_observation(self, obs: RateObservation) -> None:
        """Save rate observation to SQLite cache."""
        source_prov_str = json.dumps(obs.source_providers) if obs.source_providers else None
        deriv_path_str = json.dumps(obs.derivation_path) if obs.derivation_path else None

        sql = """
            INSERT OR REPLACE INTO exchange_rates (
                base_currency,
                quote_currency,
                observation_date,
                rate,
                provider,
                source_providers,
                source_series,
                frequency,
                derived,
                derivation_path,
                fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            obs.base.upper(),
            obs.quote.upper(),
            obs.rate_date.isoformat(),
            str(obs.rate),  # Canonical Decimal string
            obs.provider,
            source_prov_str,
            obs.source_series,
            obs.frequency,
            1 if obs.derived else 0,
            deriv_path_str,
            obs.fetched_at.isoformat(),
        )

        conn = self._get_connection()
        try:
            with conn:
                conn.execute(sql, params)
        finally:
            conn.close()

    def clear(self) -> None:
        """Clear all cached exchange rates."""
        conn = self._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM exchange_rates;")
        finally:
            conn.close()

    def _row_to_observation(self, row: sqlite3.Row, requested_date: date) -> RateObservation:
        obs_date = datetime.strptime(row["observation_date"], "%Y-%m-%d").date()
        source_provs = tuple(json.loads(row["source_providers"])) if row["source_providers"] else None
        deriv_path = tuple(json.loads(row["derivation_path"])) if row["derivation_path"] else None
        fetched_at = datetime.fromisoformat(row["fetched_at"])

        return RateObservation(
            base=row["base_currency"],
            quote=row["quote_currency"],
            rate=Decimal(row["rate"]),  # Exact Decimal reconstruction
            requested_date=requested_date,
            rate_date=obs_date,
            provider=row["provider"],
            source_providers=source_provs,
            source_series=row["source_series"],
            frequency=row["frequency"],
            derived=bool(row["derived"]),
            derivation_path=deriv_path,
            fallback_used=None,
            fetched_at=fetched_at,
        )
