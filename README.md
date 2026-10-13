# Coding Products

Python scripts for financial data analysis using Yahoo Finance.

## Scripts

### Option IV Query (`option_iv.py`)

Query the Implied Volatility (IV) of stock options.

**Features:**
- Filter by expiration date, strike price, and option type (call/put)
- Defaults to nearest expiration and most liquid contract (highest open interest)
- Verbose mode shows all available strikes with their IVs, volume, and moneyness

```bash
# Query nearest call option for AAPL
python option_iv.py AAPL

# Query a specific put option
python option_iv.py AAPL -e 2024-12-20 -t put

# Query a specific strike price
python option_iv.py AAPL -e 2024-12-20 -s 190 -t call

# Show all strikes with their IVs
python option_iv.py AAPL -e 2024-12-20 --verbose
```

| Argument | Description | Default |
|----------|-------------|---------|
| `ticker` | Stock symbol (e.g., AAPL) | Required |
| `-e, --expiration` | Option expiration date (YYYY-MM-DD) | Nearest available |
| `-s, --strike` | Specific strike price to query | Most liquid contract |
| `-t, --type` | Option type: call or put | call |
| `-v, --verbose` | Show all options with their IVs | False |

### Price Gap (`price_gap.py`)

List the price gap between current day and N days ago for given symbol(s).

```bash
# Default (30 days)
python price_gap.py AAPL GOOGL MSFT

# Custom period
python price_gap.py AAPL -d 7
```

| Argument | Description | Default |
|----------|-------------|---------|
| `tickers` | Stock symbols (e.g., AAPL GOOGL) | Required |
| `-d, --days` | Number of days to look back | 30 |

## Installation

```bash
pip install -r requirements.txt
```
