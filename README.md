<p align="center">
  <img src="C:\Users\Sande\.gemini\antigravity\scratch\global-currency\doc" width="180" alt="Global Currency Logo">
</p>

<h1 align="center">🌍 Global Currency Converter</h1>

<p align="center">
Historical • Current • Legacy Currency Conversion
<br>
High Precision Decimal Arithmetic • Complete Provenance • CLI + Python Library
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.0-orange)
![Tests](https://img.shields.io/badge/tests-21%20passed-brightgreen)

</p>

---

# Overview

**Global Currency Converter** is an open-source Python library and command-line tool for retrieving and converting **current**, **historical**, and **legacy** exchange rates with complete provenance.

It supports:

- 🌍 Current exchange rates
- 📅 Historical exchange rates
- 💱 Legacy currencies (DEM, FRF, ITL, etc.)
- 🗺 Historical country currency mapping
- 💰 High-precision `Decimal` arithmetic
- 🗄 SQLite caching
- 🔍 Complete audit trail
- ⚡ CLI + Python API

---

# Features

| Feature | Supported |
|----------|:---------:|
| Current Rates | ✅ |
| Historical Rates | ✅ |
| Legacy Currencies | ✅ |
| Historical Country Mapping | ✅ |
| Decimal Precision | ✅ |
| SQLite Cache | ✅ |
| Frankfurter API v2 | ✅ |
| BIS SDMX | ✅ |
| IMF SDMX | ✅ |
| Cross-Rate Engine | ✅ |
| CLI | ✅ |
| Python API | ✅ |

---

# Installation

## PyPI

```bash
pip install global-currency
```

## TestPyPI

```bash
pip install -i https://test.pypi.org/simple global-currency
```

---

# Quick Start

```python
from global_currency import CurrencyConverter

converter = CurrencyConverter()

result = converter.convert(
    100,
    "USD",
    "INR",
    date="2005-03-18"
)

print(result.result)
```

---

# Example Output

```text
100 USD = 4364.00 INR

Rate:             43.64

Requested Date:   2005-03-18

Rate Date:        2005-03-18

Provider:         Frankfurter

Frequency:        daily

Derived:          False
```

---

# Python API

## Historical Conversion

```python
from global_currency import CurrencyConverter

converter = CurrencyConverter()

result = converter.convert(
    100,
    "USD",
    "INR",
    date="2005-03-18"
)

print(result.result)
print(result.provider)
print(result.rate_date)
```

---

## Value Only

```python
from global_currency import convert_value

value = convert_value(
    100,
    "USD",
    "INR",
    date="2005-03-18"
)

print(value)
```

---

## Historical Country Mapping

```python
from global_currency import currency_for_country

print(currency_for_country(
    "Germany",
    date="1995-05-01"
))

print(currency_for_country(
    "Germany",
    date="2026-01-01"
))
```

---

# Command Line Interface

Convert currency

```bash
global-currency convert 100 USD INR --date 2005-03-18
```

Currency information

```bash
global-currency info DEM
```

Country lookup

```bash
global-currency country Germany --date 1995-05-01
```

---

# Architecture

```
                CurrencyConverter
                        │
                 RateResolver
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   Frankfurter       BIS SDMX       IMF SDMX
        │               │               │
        └───────────────┼───────────────┘
                        │
               Candidate Ranking
                        │
              Gap Strategy Engine
                        │
              Cross-Rate Calculator
                        │
                  SQLite Cache
                        │
               ConversionResult
```

---

# Gap Strategies

| Strategy | Description |
|----------|-------------|
| strict | Raise an error if no observation exists |
| previous | Use the previous observation |
| next | Use the next observation |
| nearest | Use the closest observation |

---

# Supported Legacy Currencies

| Currency | Country |
|----------|---------|
| DEM | Germany |
| FRF | France |
| ITL | Italy |
| ESP | Spain |
| ATS | Austria |

---

# Project Structure

```text
global_currency/

├── converter.py
├── resolver.py
├── cache.py
├── currencies.py
├── countries.py
├── providers/
│   ├── frankfurter.py
│   ├── bis.py
│   └── imf.py
├── data/
└── tests/
```

---

# Roadmap

- [x] Historical exchange rates
- [x] Legacy currencies
- [x] SQLite cache
- [x] Frankfurter v2
- [x] BIS provider
- [x] IMF provider
- [ ] Async support
- [ ] Pandas integration
- [ ] CSV export
- [ ] Graph plotting

---

# License

Released under the **MIT License**.