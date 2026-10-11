# Option IV Query

A Python script to query the Implied Volatility (IV) of stock options using Yahoo Finance data.

## Features

- Query IV for any publicly traded stock with options
- Filter by expiration date, strike price, and option type (call/put)
- Defaults to nearest expiration and most liquid contract (highest open interest)
- Verbose mode shows all available strikes with their IVs, volume, and moneyness

## Installation

```bash
pip install -r requirements.txt
```

## Usage

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

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `ticker` | Stock symbol (e.g., AAPL) | Required |
| `-e, --expiration` | Option expiration date (YYYY-MM-DD) | Nearest available |
| `-s, --strike` | Specific strike price to query | Most liquid contract |
| `-t, --type` | Option type: call or put | call |
| `-v, --verbose` | Show all options with their IVs | False |

## Example Output

```
Ticker:       AAPL
Expiration:   2024-12-20
Type:         CALL
Spot Price:   $195.71
Strike:       $190.00
Last Price:   $8.50
Volume:       1234
Open Interest:5678

Implied Volatility (IV): 28.45%
```
