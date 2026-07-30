"""Historical conversion and cross-rate audit example."""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from global_currency import CurrencyConverter

def main():
    print("=== Global Currency Historical & Cross-Rate Example ===")
    converter = CurrencyConverter()

    # Derived Cross-Rate Conversion (e.g., INR to JPY on 2005-03-18)
    res = converter.convert(1000, "INR", "JPY", date_val="2005-03-18", fallback="previous")
    print(f"\nConverted 1000 INR to {res.result} JPY on {res.requested_date}")
    print(f"Derived:         {res.derived}")
    print(f"Derivation Path: {res.derivation_path}")
    print(f"Provider:        {res.provider}")

    if res.source_observations:
        print("\nUnderlying Pivot Observations:")
        for idx, child in enumerate(res.source_observations, 1):
            print(f"  [{idx}] {child.base}/{child.quote} = {child.rate} ({child.provider}, Date: {child.rate_date})")

if __name__ == "__main__":
    main()
