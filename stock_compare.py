#!/usr/bin/env python3
"""
Stock Price Comparison Script
Compares price change delta of any 2 given stock symbols over the last 30 days.
"""

import yfinance as yf
from datetime import datetime, timedelta
import sys

def get_stock_data(symbol, period="30d"):
    """Fetch stock data for a given symbol"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_price_change(data):
    """Calculate price change percentage from first to last available price"""
    if data is None or len(data) == 0:
        return None
    
    open_price = data['Open'].iloc[0]
    close_price = data['Close'].iloc[-1]
    
    if open_price != 0:
        percent_change = ((close_price - open_price) / open_price) * 100
        return round(percent_change, 2)
    else:
        return None

def compare_stocks(symbol1, symbol2):
    """Compare price changes for two stocks over last 30 days"""
    
    print(f"Comparing {symbol1} vs {symbol2} (last 30 days)")
    print("-" * 50)
    
    # Get data for both stocks
    stock1_data = get_stock_data(symbol1)
    stock2_data = get_stock_data(symbol2)
    
    if stock1_data is None or stock2_data is None:
        return
    
    # Calculate price changes
    change1 = calculate_price_change(stock1_data)
    change2 = calculate_price_change(stock2_data)
    
    print(f"{symbol1} 30-day change: {change1}%")
    print(f"{symbol2} 30-day change: {change2}%")
    
    if change1 is not None and change2 is not None:
        delta = abs(change1 - change2)
        print(f"Price change difference: {delta:.2f}%")
        
        if change1 > change2:
            print(f"{symbol1} outperformed {symbol2} by {delta:.2f}%")
        elif change2 > change1:
            print(f"{symbol2} outperformed {symbol1} by {delta:.2f}%")
        else:
            print("Both stocks performed equally")

def main():
    if len(sys.argv) != 3:
        print("Usage: python stock_compare.py <stock_symbol_1> <stock_symbol_2>")
        print("Example: python stock_compare.py AAPL MSFT")
        return
    
    symbol1 = sys.argv[1].upper()
    symbol2 = sys.argv[2].upper()
    
    compare_stocks(symbol1, symbol2)

if __name__ == "__main__":
    main()