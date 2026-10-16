import yfinance as yf
import argparse
from datetime import datetime, timedelta


def load_symbol_list(path: str) -> list[str]:
    """Read symbols from a file, one per line. Blank lines and # comments are ignored."""
    symbols = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            symbols.append(line.split()[0].upper())
    return symbols


def get_price_gap(tickers: list[str], period_days: int = 30):
    """
    Display the price gap between current day and N days ago for given symbol(s).

    Args:
        tickers: List of stock symbols (e.g., ['AAPL', 'GOOGL'])
        period_days: Number of days to look back (default: 30)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)

    print(f"\n{'Symbol':<12} {'Price Today':>12} {'{days} Ago':>14} {'Gap (Abs)':>12} {'Gap (%)':>10}".format(days=period_days))
    print("-" * 62)

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))

            if hist.empty:
                print(f"{ticker:<12} {'No data available':>50}")
                continue

            price_today = hist.iloc[-1]["Close"]
            price_old = hist.iloc[0]["Close"]
            gap_abs = price_today - price_old
            gap_pct = (gap_abs / price_old) if price_old != 0 else 0

            print(f"{ticker:<12} ${price_today:>10.2f} ${price_old:>12.2f} ${gap_abs:>+10.2f} {gap_pct:>+9.2%}")
        except Exception as e:
            print(f"{ticker:<12} {'Error':>50}")


def main():
    parser = argparse.ArgumentParser(
        description="List price gap between current day and N days ago for given symbol(s)."
    )
    parser.add_argument("tickers", nargs="*", help="Stock symbols (e.g., AAPL GOOGL MSFT)")
    parser.add_argument("-f", "--file", help="Path to a symbol list file (one symbol per line)")
    parser.add_argument("-d", "--days", type=int, default=30, help="Number of days to look back (default: 30)")

    args = parser.parse_args()

    if args.file and args.tickers:
        parser.error("provide either tickers or --file, not both")

    if args.file:
        try:
            tickers = load_symbol_list(args.file)
        except OSError as e:
            parser.error(f"Could not read symbol list {args.file}: {e}")
        if not tickers:
            parser.error(f"No symbols found in {args.file}")
    elif args.tickers:
        tickers = [t.upper() for t in args.tickers]
    else:
        parser.error("provide at least one ticker or --file")

    get_price_gap(tickers, args.days)


if __name__ == "__main__":
    main()
