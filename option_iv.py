import yfinance as yf
import argparse


def get_option_iv(ticker: str, expiration: str = None, strike: float = None, call_put: str = "call", verbose: bool = False):
    """
    Query the Implied Volatility (IV) of a stock option.

    Args:
        ticker: Stock symbol (e.g., 'AAPL')
        expiration: Option expiration date in YYYY-MM-DD format. If None, uses nearest expiration.
        strike: Specific strike price to query. If None, uses most liquid contract.
        call_put: 'call' or 'put'
        verbose: Print all available options with their IVs
    """
    stock = yf.Ticker(ticker)

    if not expiration:
        dates = stock.options
        if not dates:
            print(f"No options data available for {ticker}")
            return
        expiration = dates[0]
        print(f"Using nearest expiration: {expiration}\n")

    option_chain = stock.option_chain(expiration)
    calls = option_chain.calls
    puts = option_chain.puts

    if call_put.lower() in ("call", "c"):
        data = calls
    elif call_put.lower() in ("put", "p"):
        data = puts
    else:
        print(f"Invalid type '{call_put}'. Use 'call' or 'put'.")
        return

    if data.empty:
        print(f"No {call_put} options available for expiration {expiration}")
        return

    try:
        spot = stock.fast_info.last_price
    except Exception:
        spot = None

    if verbose:
        print(f"\n{'Strike':>10} {'Last Price':>12} {'Bid':>10} {'Ask':>10} {'Volume':>10} "
              f"{'Open Int':>10} {'IV':>8} {'In The Money':>15}")
        print("-" * 90)
        for _, row in data.iterrows():
            iv = row.get("impliedVolatility", None)
            if iv is not None:
                iv_str = f"{iv:.2%}"
            else:
                iv_str = "N/A"

            itm = ""
            if spot is not None:
                if call_put.lower() in ("call", "c") and row["strike"] <= spot:
                    itm = "Yes"
                elif call_put.lower() in ("put", "p") and row["strike"] >= spot:
                    itm = "Yes"
                else:
                    itm = "No"

            print(f"{row['strike']:>10.2f} {row.get('lastPrice', 0):>12.2f} "
                  f"{row.get('bid', 0):>10.2f} {row.get('ask', 0):>10.2f} "
                  f"{row.get('volume', 0):>10.0f} {row.get('openInterest', 0):>10.0f} "
                  f"{iv_str:>8} {itm:>15}")

        return data

    if strike is not None:
        filtered = data[data["strike"] == strike]
        if filtered.empty:
            print(f"No {call_put} option found for strike ${strike:.2f} on expiration {expiration}")
            return
        most_liquid = filtered.iloc[0]
    elif "openInterest" in data.columns and not data["openInterest"].isna().all():
        most_liquid = data.loc[data["openInterest"].idxmax()]
    else:
        most_liquid = data.iloc[0]

    iv = most_liquid.get("impliedVolatility", None)
    strike_price = most_liquid.get("strike", None)
    last_price = most_liquid.get("lastPrice", None)
    volume = most_liquid.get("volume", 0)
    open_interest = most_liquid.get("openInterest", 0)

    print(f"\nTicker:       {ticker}")
    print(f"Expiration:   {expiration}")
    print(f"Type:         {call_put.upper()}")
    if spot is not None:
        print(f"Spot Price:   ${spot:.2f}")
    print(f"Strike:       ${strike_price:.2f}" if strike_price else "Strike:       N/A")
    print(f"Last Price:   ${last_price:.2f}" if last_price else "Last Price:   N/A")
    print(f"Volume:       {volume}")
    print(f"Open Interest:{open_interest}")

    if iv is not None:
        print(f"\nImplied Volatility (IV): {iv:.2%}")
    else:
        print("\nImplied Volatility (IV): N/A")

    return data


def main():
    parser = argparse.ArgumentParser(description="Query the Implied Volatility (IV) of a stock option.")
    parser.add_argument("ticker", help="Stock symbol (e.g., AAPL)")
    parser.add_argument("-e", "--expiration", default=None, help="Option expiration date (YYYY-MM-DD). Defaults to nearest.")
    parser.add_argument("-s", "--strike", type=float, default=None, help="Specific strike price to query.")
    parser.add_argument("-t", "--type", choices=["call", "put"], default="call", help="Option type: call or put (default: call)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all options with their IVs")

    args = parser.parse_args()
    get_option_iv(args.ticker, args.expiration, args.strike, args.type, args.verbose)


if __name__ == "__main__":
    main()
