# Global Historical Currency Converter (`global-currency`)

An open-source Python library and CLI for retrieving and converting current and historical exchange rates across active and legacy world currencies (e.g. `USD`, `EUR`, `INR`, `DEM`, `FRF`).

## Highlights

- **Strict Accuracy**: Never invents or silently fabricates missing exchange rates.
- **Complete Provenance**: Records provider, source series, contributing providers, observation frequency (`daily`, `monthly`, `quarterly`, `annual`), and fallback strategy used.
- **Decimal Math**: All exchange rate calculations use Python's `Decimal` module for financial precision.
- **SQLite Caching**: Caching using `TEXT` representation for `Decimal` numbers.
- **RateResolver & Fallbacks**: Configurable candidate ranking across Frankfurter API v2, BIS SDMX, IMF SDMX, and local cache with gap handling (`strict`, `previous`, `next`, `nearest`).
- **Cross-Currency Pivot Engine**: Full auditability for derived rates (`INR -> USD -> JPY`) with `source_observations`.
- **Historical Country Mappings**: Look up historical active currency for any country on a specific date (e.g. Germany in 1995 -> `DEM`, Germany in 2026 -> `EUR`).

## Installation

```bash
pip install global-currency
```

## Python API Usage

### Current & Historical Conversion

```python
from global_currency import CurrencyConverter, convert, convert_value

c = CurrencyConverter()

# Basic Conversion (returns ConversionResult object)
result = c.convert(100, "USD", "INR", date="2005-03-18")
print(result.result)         # Decimal('4360.20000000')
print(result.provider)       # 'Frankfurter'
print(result.rate_date)      # datetime.date(2005, 3, 18)
print(result.frequency)      # 'daily'

# Value Only Shortcut
val = convert_value(100, "USD", "INR", date="2005-03-18")
print(val)                   # Decimal('4360.20000000')
```

### Country Currency Lookup

```python
from global_currency import currency_for_country

print(currency_for_country("Germany", date="1995-05-01"))  # "DEM"
print(currency_for_country("Germany", date="2026-01-01"))  # "EUR"
```

## CLI Usage

```bash
global-currency convert 100 USD INR --date 2005-03-18
global-currency info DEM
global-currency country Germany --date 1995-05-01
```
