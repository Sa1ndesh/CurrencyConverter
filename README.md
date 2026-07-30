# 🌍 Global Currency v1.0.0

[![CI](https://github.com/Sa1ndesh/CurrencyConverter/actions/workflows/ci.yml/badge.svg)](https://github.com/Sa1ndesh/CurrencyConverter/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/global-currency.svg)](https://pypi.org/project/global-currency/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://pypi.org/project/global-currency/)


**Global Currency** is a production-ready, open-source Python library and CLI tool for current and historical currency conversions across active and legacy world currencies. Built with multi-provider failover, strict Decimal precision, multi-tiered caching (Memory & SQLite), async support, and historical charting capabilities.

---

## 🚀 Features

- **Clean API**: Direct shortcuts (`convert`, `convert_value`, `get_rate`, `currency_info`, `format_currency`).
- **Exact Precision**: Stores and calculates using Python's `Decimal` type to avoid floating-point errors.
- **Historical Rates**: Query historical exchange rates back decades with configurable weekend/holiday gap strategies (`previous`, `next`, `nearest`, `strict`).
- **Multi-Provider Failover**: Automatic fallback between Frankfurter, ECB, BIS, IMF, and ExchangeRateHost data sources.
- **Fast Caching**: Multi-tiered caching (In-Memory TTL Cache & SQLite persistent disk cache).
- **Async Support**: Native non-blocking `AsyncCurrencyConverter` for high-throughput asynchronous applications.
- **Historical Charts**: Render line graphs of historical exchange rates powered by `matplotlib`.
- **Currency Formatting**: Localized formatting (e.g., `₹12,345.67`, `$100.00`).
- **Powerful CLI**: Execute conversions and lookups directly from your terminal.

---

## 📦 Installation

Install via `pip`:

```bash
pip install global-currency
```

To enable historical charting support:

```bash
pip install global-currency[charts]
```

---

## ⚡ Quick Start

### 1. Direct Function Shortcuts

```python
from global_currency import convert, convert_value, get_rate

# Current conversion
result = convert(100, "USD", "INR")
print(f"100 USD = {result.result} INR (Rate: {result.rate})")

# Get raw Decimal conversion value directly
val = convert_value(100, "USD", "EUR")
print(val)  # e.g., Decimal('92.15')

# Retrieve rate observation metadata
obs = get_rate("USD", "JPY")
print(f"Provider: {obs.provider}, Date: {obs.rate_date}")
```

### 2. Historical Conversion

Both `date` and `date_val` parameter names are supported:

```python
from global_currency import convert

# Historical conversion on a specific date
res = convert(100, "USD", "INR", date="2005-03-18")

print("Converted Amount :", res.result)
print("Exchange Rate    :", res.rate)
print("Rate Date        :", res.rate_date)
print("Provider         :", res.provider)
```

---

## ℹ️ Currency Information & Formatting

### Get Currency Details

```python
from global_currency import currency_info

info = currency_info("USD")
print(info.name)    # US Dollar
print(info.symbol)  # $
print(info.code)    # USD
```

### Format Currency

```python
from global_currency import format_currency

print(format_currency(12345.67, "INR"))  # ₹12,345.67
print(format_currency(100, "USD"))       # $100.00
```

---

## 📈 Historical Charts

Generate and save visual line charts of historical rate series:

```python
from global_currency import CurrencyConverter

converter = CurrencyConverter()
converter.plot_history(
    "USD",
    "INR",
    start_date="2024-01-01",
    end_date="2024-12-31",
    save_path="usd_inr_2024.png"
)
```

---

## ⚡ Async Support

For async applications (FastAPI, asyncio, etc.):

```python
import asyncio
from global_currency import AsyncCurrencyConverter

async def main():
    converter = AsyncCurrencyConverter()
    result = await converter.convert(100, "USD", "EUR")
    print("Async result:", result.result)

asyncio.run(main())
```

---

## 💻 Command-Line Tool (CLI)

After installation, use the `global-currency` CLI:

```bash
# Convert current currency
global-currency convert 100 USD INR
# Output: 100 USD = ₹8,650.21 INR

# Historical conversion
global-currency convert 100 USD INR --date 2005-03-18

# Full provenance details
global-currency convert 100 USD EUR --details

# Currency lookup & list
global-currency info USD
global-currency currencies --active-only
global-currency country Germany
```

---

## 🛡️ Multi-Provider Fallback Architecture

`global-currency` automatically resolves exchange rates across multiple data sources:
1. **Frankfurter** (ECB reference rates)
2. **ECB** (European Central Bank official feed)
3. **BIS** (Bank for International Settlements)
4. **IMF** (International Monetary Fund SDR rates)
5. **ExchangeRateHost**

If one provider is offline or lacks coverage for a specific date or currency pair, the resolver automatically queries the next provider or computes synthetic cross-rates via pivot currencies (e.g., USD/EUR).

---

## 🚨 Error Handling

All exceptions derive from `CurrencyError`:

```python
from global_currency import convert
from global_currency.exceptions import (
    UnsupportedCurrencyError,
    InvalidDateError,
    HistoricalRateNotFound
)

try:
    res = convert(100, "XYZ", "INR")
except UnsupportedCurrencyError as e:
    print("Invalid currency code:", e)
except InvalidDateError as e:
    print("Invalid date format:", e)
except HistoricalRateNotFound as e:
    print("Rate not available:", e)
```

---

## 📄 License

Distributed under the MIT License. See [LICENSE](file:///c:/Users/Sande/Desktop/global-currency/LICENSE) for more details.

---

## 🤝 Contributing

Contributions are welcome! Check out [CONTRIBUTING.md](file:///c:/Users/Sande/Desktop/global-currency/CONTRIBUTING.md) to get started.