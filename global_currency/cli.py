"""Command-Line Interface for global-currency package."""

import argparse
import sys
from decimal import Decimal

from global_currency.countries import currency_for_country
from global_currency.currencies import currency_info, list_currencies
from global_currency.exceptions import CurrencyError
from global_currency.converter import CurrencyConverter, convert, convert_value, get_rate, history


def main():
    parser = argparse.ArgumentParser(
        prog="global-currency",
        description="Global Historical Currency Converter CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: convert
    convert_parser = subparsers.add_parser("convert", help="Convert currency amount")
    convert_parser.add_argument("amount", type=str, help="Monetary amount to convert")
    convert_parser.add_argument("from_currency", type=str, help="Source currency code (e.g. USD)")
    convert_parser.add_argument("to_currency", type=str, help="Target currency code (e.g. INR)")
    convert_parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format", default=None)
    convert_parser.add_argument(
        "--fallback",
        choices=["previous", "next", "nearest", "strict"],
        default="previous",
        help="Gap strategy for weekends/holidays (default: previous)"
    )
    convert_parser.add_argument("--details", action="store_true", help="Print complete provenance details")

    # Subcommand: info
    info_parser = subparsers.add_parser("info", help="Get currency metadata")
    info_parser.add_argument("code", type=str, help="Currency ISO code (e.g. DEM, INR)")

    # Subcommand: currencies
    curr_parser = subparsers.add_parser("currencies", help="List supported currencies")
    curr_parser.add_argument("--active-only", action="store_true", help="Filter to active currencies only")

    # Subcommand: country
    country_parser = subparsers.add_parser("country", help="Lookup currency for a country")
    country_parser.add_argument("country_name", type=str, help="Country name (e.g. Germany)")
    country_parser.add_argument("--date", type=str, help="Date YYYY-MM-DD for historical validity lookup", default=None)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "convert":
            if args.details:
                res = convert(
                    amount=args.amount,
                    from_currency=args.from_currency,
                    to_currency=args.to_currency,
                    date=args.date,
                    fallback=args.fallback
                )
                print(f"{res.amount} {res.from_currency} = {res.result} {res.to_currency}")
                print(f"Rate:             {res.rate}")
                print(f"Requested Date:   {res.requested_date}")
                print(f"Rate Date:        {res.rate_date}")
                print(f"Provider:         {res.provider}")
                if res.source_providers:
                    print(f"Source Providers: {', '.join(res.source_providers)}")
                if res.source_series:
                    print(f"Source Series:    {res.source_series}")
                print(f"Frequency:        {res.frequency}")
                print(f"Derived:          {res.derived}")
                if res.derivation_path:
                    print(f"Derivation Path:  {' -> '.join(res.derivation_path)}")
                if res.fallback_used:
                    print(f"Fallback Used:    {res.fallback_used}")
            else:
                val = convert_value(
                    amount=args.amount,
                    from_currency=args.from_currency,
                    to_currency=args.to_currency,
                    date=args.date,
                    fallback=args.fallback
                )
                from global_currency.formatting import format_currency
                formatted_target = format_currency(val, args.to_currency)
                print(f"{args.amount} {args.from_currency.upper()} = {formatted_target} {args.to_currency.upper()}")


        elif args.command == "info":
            info = currency_info(args.code)
            print(f"Code:         {info.code}")
            print(f"Name:         {info.name}")
            print(f"Symbol:       {info.symbol}")
            print(f"Numeric Code: {info.numeric_code}")
            print(f"Active:       {info.active}")
            if info.start_date:
                print(f"Start Date:   {info.start_date}")
            if info.end_date:
                print(f"End Date:     {info.end_date}")

        elif args.command == "currencies":
            currs = list_currencies(active_only=args.active_only)
            print(f"{'Code':<6} {'Name':<30} {'Active':<8} {'Symbol'}")
            print("-" * 50)
            for c in currs:
                print(f"{c.code:<6} {c.name:<30} {str(c.active):<8} {c.symbol}")

        elif args.command == "country":
            curr_code = currency_for_country(args.country_name, date=args.date)
            date_str = f" on {args.date}" if args.date else ""
            print(f"Currency for {args.country_name}{date_str}: {curr_code}")

    except CurrencyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
