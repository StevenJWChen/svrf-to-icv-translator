#!/usr/bin/env python3
"""
TSMC Stock Data Fetcher
Fetches current and historical stock data for Taiwan Semiconductor Manufacturing Company (TSM)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import argparse
import sys

def fetch_current_price(ticker="TSM"):
    """Fetch current TSMC stock price and basic info"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        print(f"\n=== TSMC ({ticker}) Current Stock Information ===")
        print(f"Company Name: {info.get('longName', 'N/A')}")
        print(f"Current Price: ${info.get('currentPrice', 'N/A')}")
        print(f"Previous Close: ${info.get('previousClose', 'N/A')}")
        print(f"Day High: ${info.get('dayHigh', 'N/A')}")
        print(f"Day Low: ${info.get('dayLow', 'N/A')}")
        print(f"Volume: {info.get('volume', 'N/A'):,}")
        print(f"Market Cap: ${info.get('marketCap', 'N/A'):,}")
        print(f"52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
        print(f"52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"Error fetching current price: {e}")
        return False

def fetch_historical_data(ticker="TSM", period="1y"):
    """Fetch historical stock data for TSMC"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            print("No historical data found")
            return False
            
        print(f"\n=== TSMC ({ticker}) Historical Data ({period}) ===")
        print(f"Data from {hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}")
        print(f"\nSummary Statistics:")
        print(f"Highest Close: ${hist['Close'].max():.2f}")
        print(f"Lowest Close: ${hist['Close'].min():.2f}")
        print(f"Average Close: ${hist['Close'].mean():.2f}")
        print(f"Latest Close: ${hist['Close'][-1]:.2f}")
        
        print(f"\nRecent 10 days:")
        recent_data = hist.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']]
        recent_data['Close'] = recent_data['Close'].round(2)
        recent_data['Open'] = recent_data['Open'].round(2)
        recent_data['High'] = recent_data['High'].round(2)
        recent_data['Low'] = recent_data['Low'].round(2)
        print(recent_data.to_string())
        
        return hist
    except Exception as e:
        print(f"Error fetching historical data: {e}")
        return False

def save_to_csv(data, filename="tsmc_historical_data.csv"):
    """Save historical data to CSV file"""
    try:
        data.to_csv(filename)
        print(f"\nHistorical data saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Fetch TSMC stock data")
    parser.add_argument("--current", action="store_true", help="Fetch current stock price")
    parser.add_argument("--history", action="store_true", help="Fetch historical data")
    parser.add_argument("--period", default="1y", help="Historical data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    parser.add_argument("--save", action="store_true", help="Save historical data to CSV")
    parser.add_argument("--ticker", default="TSM", help="Stock ticker symbol (default: TSM)")
    
    args = parser.parse_args()
    
    if not args.current and not args.history:
        args.current = True
        args.history = True
    
    try:
        if args.current:
            fetch_current_price(args.ticker)
        
        if args.history:
            hist_data = fetch_historical_data(args.ticker, args.period)
            if hist_data is not False and args.save:
                save_to_csv(hist_data, f"{args.ticker.lower()}_historical_data.csv")
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()