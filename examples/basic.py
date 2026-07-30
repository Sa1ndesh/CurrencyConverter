"""Basic usage example for global-currency package."""

import sys

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from global_currency import CurrencyConverter, convert, convert_value, currency_for_country, currency_info

def main():
    print("=== Global Currency Basic Example ===")

    # 1. Currency info lookup
    info_inr = currency_info("INR")
    print(f"Currency: {info_inr.name} ({info_inr.code}), Symbol: {info_inr.symbol}")

    info_dem = currency_info("DEM")
    print(f"Legacy Currency: {info_dem.name} ({info_dem.code}), Active: {info_dem.active}")

    # 2. Historical Country Lookup
    dem_curr = currency_for_country("Germany", date="1995-05-01")
    eur_curr = currency_for_country("Germany", date="2026-01-01")
    print(f"Germany in 1995: {dem_curr}")
    print(f"Germany in 2026: {eur_curr}")

    # 3. Conversion with full provenance details
    res = convert(100, "USD", "INR", date="2005-03-18", fallback="previous")
    print("\n--- Conversion Result ---")
    print(f"Amount:          {res.amount} {res.from_currency}")
    print(f"Result:          {res.result} {res.to_currency}")
    print(f"Exchange Rate:   {res.rate}")
    print(f"Requested Date:  {res.requested_date}")
    print(f"Market Date:     {res.rate_date}")
    print(f"Provider:        {res.provider}")
    if res.source_providers:
        print(f"Source Providers:{', '.join(res.source_providers)}")
    print(f"Source Series:   {res.source_series}")
    print(f"Frequency:       {res.frequency}")
    print(f"Fallback Used:   {res.fallback_used}")

if __name__ == "__main__":
    main()
