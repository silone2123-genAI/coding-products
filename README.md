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

### Stock Compare (`stock_compare.py`)

Compare the 30-day price change of any two stock symbols.

```bash
# Compare AAPL vs MSFT over the last 30 days
python stock_compare.py AAPL MSFT
```

| Argument | Description | Default |
|----------|-------------|---------|
| `stock_symbol_1` | First stock symbol (e.g., AAPL) | Required |
| `stock_symbol_2` | Second stock symbol (e.g., MSFT) | Required |

Reports each symbol's 30-day price change, the absolute difference between them, and which one outperformed.

### Portfolio Export (`portfolio_export.py`)

Export a Yahoo Finance portfolio's holdings and prices to CSV.

Authenticates through a persistent Playwright browser — on first run a browser
opens for you to sign in once; the session is cached in `.yahoo_session/` and
reused on later runs.

```bash
python portfolio_export.py                    # default: p_4 portfolio
python portfolio_export.py -u <pf_url>        # a different portfolio
python portfolio_export.py --no-enrich        # skip yfinance company-name enrichment
python portfolio_export.py --headless         # reuse logged-in session without opening a window
```

Output is `portfolio_p<id>_<timestamp>.csv`. A raw copy of Yahoo's portfolio
API JSON (when captured) is also saved into `.yahoo_session/`.

| Argument | Description | Default |
|----------|-------------|---------|
| `-u, --url` | Portfolio URL to export | `.../portfolio/p_4/view/v1` |
| `-o, --output` | Output CSV path | `portfolio_p<id>_<timestamp>.csv` |
| `--headless` | Run browser headless (session must be logged in) | False |
| `--no-enrich` | Skip yfinance company-name enrichment | False |

First run:

```bash
pip install -r requirements.txt
python -m playwright install chromium
python portfolio_export.py   # sign in when the browser opens
```

## Installation

```bash
pip install -r requirements.txt
python -m playwright install chromium
```
