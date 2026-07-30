"""Tests for matplotlib historical charts plotting."""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from global_currency import CurrencyConverter
from global_currency.models import RateObservation


class MockChartProvider:
    name = "MockChartProvider"

    def supports(self, currency):
        return True

    def get_rate(self, base, quote, target_date, provider_pin=None):
        return None

    def get_series(self, base, quote, start_date, end_date):
        return [
            RateObservation(
                base=base,
                quote=quote,
                rate=Decimal("82.50"),
                requested_date=start_date,
                rate_date=start_date,
                provider=self.name,
            ),
            RateObservation(
                base=base,
                quote=quote,
                rate=Decimal("83.10"),
                requested_date=end_date,
                rate_date=end_date,
                provider=self.name,
            ),
        ]


def test_plot_history_save(tmp_path):
    converter = CurrencyConverter(providers=[MockChartProvider()])
    out_file = tmp_path / "chart.png"

    # Test plot_history with save_path
    try:
        res_path = converter.plot_history("USD", "INR", "2024-01-01", "2024-01-02", save_path=str(out_file))
        assert res_path == str(out_file)
        assert out_file.exists()
    except ImportError:
        # If matplotlib is not installed in the test environment, ensure graceful error handling
        pytest.skip("matplotlib not installed in test environment")
