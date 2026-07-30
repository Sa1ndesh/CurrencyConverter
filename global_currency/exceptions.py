"""Custom exceptions for global-currency."""


class CurrencyError(Exception):
    """Base exception for all currency-related errors."""
    pass


class UnsupportedCurrencyError(CurrencyError):
    """Raised when an invalid or unsupported currency code is supplied."""
    pass


class HistoricalRateNotFound(CurrencyError):
    """Raised when no rate observation exists for the requested parameters and strategy."""
    pass


class InvalidDateError(CurrencyError):
    """Raised when an invalid date string or object is provided."""
    pass


class ProviderUnavailableError(CurrencyError):
    """Raised when an exchange rate provider fails or times out."""
    pass


class InvalidAmountError(CurrencyError):
    """Raised when an invalid currency amount is supplied."""
    pass
