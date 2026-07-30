# Changelog

All notable changes to the `global-currency` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-30

### Added
- **Direct Function Shortcuts**: Convenience top-level imports for `convert`, `convert_value`, `get_rate`, `history`, `currency_info`, and `format_currency`.
- **Dual Date Parameters**: Supported both `date` and `date_val` keyword parameters across all API endpoints for 100% backward compatibility.
- **Async Support**: Added `AsyncCurrencyConverter` class for asynchronous applications.
- **Currency Formatting**: Added `format_currency(amount, currency_code)` helper supporting symbols (e.g., `₹`, `$`, `€`) and standard number formatting.
- **Historical Charts**: Added `converter.plot_history()` using `matplotlib` to render historical rate series graphs.
- **Multi-tiered Fast Caching**: Added `MemoryCache` with TTL expiration alongside persistent `SQLiteCache`.
- **Expanded Providers**: Added `ECBProvider` (European Central Bank) and `ExchangeRateHostProvider` with automatic fallback.
- **Enhanced CLI**: Clean formatted output (`100 USD = ₹8,650.21 INR`) and new commands for information, currency listing, and country lookup.
- **Governance & CI**: Added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, Dependabot config, CodeQL analysis, and complete GitHub Actions CI workflow.

## [0.1.4] - 2026-07-30
- Multi-provider fallback support with Frankfurter, BIS, and IMF providers.
- SQLite persistence layer for offline rate caching.
