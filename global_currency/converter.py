from global_currency import CurrencyConverter
from datetime import date

# Create converter object
converter = CurrencyConverter()

# Convert 1 USD to INR on 18 March 2005
result = converter.convert(
    amount=1,
    from_currency="USD",
    to_currency="INR",
    date_val=date(2005, 3, 18)
)

# Print results
print("Converted Amount :", result.result)
print("Exchange Rate    :", result.rate)
print("Rate Date        :", result.rate_date)
print("Provider         :", result.provider)