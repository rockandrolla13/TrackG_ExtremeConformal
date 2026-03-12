#!/usr/bin/env python3
"""
Download equity and index data from Yahoo Finance.

Downloads major indices and tech stocks with full historical coverage.
Covers all major equity extreme events: 2008 crisis, 2010 flash crash, 2020 COVID.

Source: Yahoo Finance (via yfinance library)
Output: CSV files in data/equities/raw/
Exit code: 0 on success, 1 on failure
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    import yfinance as yf
except ImportError as e:
    print(f"ERROR: Missing required library: {e}")
    print("Install with: pip install yfinance pandas")
    sys.exit(1)


OUTPUT_DIR = Path("data/equities/raw")
START_DATE = "2000-01-01"
END_DATE = "2024-12-31"

# Major indices
INDICES = {
    "^GSPC": "SP500",      # S&P 500
    "^IXIC": "NASDAQ",     # NASDAQ Composite
    "^DJI": "DJIA",        # Dow Jones Industrial Average
    "^RUT": "RUSSELL2000", # Russell 2000
}

# Major tech stocks (for 2020+ analysis)
TECH_STOCKS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "GOOGL",  # Alphabet (Google)
    "AMZN",   # Amazon
    "TSLA",   # Tesla
    "NVDA",   # NVIDIA
    "META",   # Meta (Facebook)
    "NFLX",   # Netflix
]

# Financial stocks (for 2008 crisis)
FINANCIAL_STOCKS = [
    "JPM",    # JPMorgan Chase
    "BAC",    # Bank of America
    "GS",     # Goldman Sachs
    "C",      # Citigroup
    "WFC",    # Wells Fargo
]

# Other notable stocks
OTHER_STOCKS = [
    "SPY",    # SPDR S&P 500 ETF (most liquid)
    "QQQ",    # Invesco QQQ (NASDAQ-100)
    "DIA",    # SPDR Dow Jones Industrial Average ETF
    "IWM",    # iShares Russell 2000 ETF
]


def download_ticker(symbol: str, name: str | None = None) -> bool:
    """Download daily OHLCV data for a single ticker."""
    if name is None:
        name = symbol

    output_file = OUTPUT_DIR / f"{name}_daily_{START_DATE.replace('-', '')}_{END_DATE.replace('-', '')}.csv"

    # Check if already exists
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 0.01:  # > 10KB
            print(f"  ✓ {name:12s} - already exists ({file_size_mb:.2f} MB)")
            return True

    try:
        print(f"  ⬇ {name:12s} - downloading...", end=" ", flush=True)

        # Download data
        ticker = yf.Ticker(symbol)
        df = ticker.history(
            start=START_DATE,
            end=END_DATE,
            auto_adjust=False,
            actions=False
        )

        if df.empty:
            print(f"✗ NO DATA")
            return False

        # Prepare DataFrame
        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]

        # Rename columns to standard format
        column_mapping = {
            'date': 'datetime',
            'datetime': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
        }

        df = df.rename(columns=column_mapping)

        # Select required columns
        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

        # Convert datetime to string
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d')

        # Save to CSV
        df.to_csv(output_file, index=False)

        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"✓ {len(df):,} rows ({file_size_mb:.2f} MB)")

        return True

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def verify_extreme_events(symbol: str, name: str) -> None:
    """Verify that extreme events are present in the data."""
    output_file = OUTPUT_DIR / f"{name}_daily_{START_DATE.replace('-', '')}_{END_DATE.replace('-', '')}.csv"

    if not output_file.exists():
        return

    df = pd.read_csv(output_file)
    df['datetime'] = pd.to_datetime(df['datetime'])

    extreme_events = [
        ("2008-09-29", "Lehman Brothers collapse"),
        ("2010-05-06", "Flash Crash"),
        ("2015-08-24", "China market crash"),
        ("2018-02-05", "VIXplosion"),
        ("2020-03-16", "COVID-19 crash (peak)"),
        ("2020-03-23", "COVID-19 bottom"),
    ]

    print(f"\n  Extreme events in {name}:")
    for event_date, event_name in extreme_events:
        event_dt = pd.to_datetime(event_date)
        if event_dt in df['datetime'].values:
            row = df[df['datetime'] == event_dt].iloc[0]
            change_pct = ((row['close'] - row['open']) / row['open']) * 100
            print(f"    ✓ {event_date}: {event_name}")
            print(f"       Close: {row['close']:.2f}, Change: {change_pct:+.2f}%")
        else:
            print(f"    ⚠ {event_date}: {event_name} - NOT FOUND")


def main() -> int:
    """Download all equity data from Yahoo Finance."""
    print("="*70)
    print("Equity Data Download - Yahoo Finance")
    print("="*70)
    print(f"Source: Yahoo Finance (yfinance library)")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Output: {OUTPUT_DIR}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}\n")

    # Track failures
    failed = []
    successful = 0

    # Download indices
    print("="*70)
    print("MAJOR INDICES")
    print("="*70)

    for symbol, name in INDICES.items():
        if download_ticker(symbol, name):
            successful += 1
        else:
            failed.append((symbol, name))

    # Download tech stocks
    print("\n" + "="*70)
    print("TECH STOCKS (2020+ analysis)")
    print("="*70)

    for symbol in TECH_STOCKS:
        if download_ticker(symbol):
            successful += 1
        else:
            failed.append((symbol, symbol))

    # Download financial stocks
    print("\n" + "="*70)
    print("FINANCIAL STOCKS (2008 crisis)")
    print("="*70)

    for symbol in FINANCIAL_STOCKS:
        if download_ticker(symbol):
            successful += 1
        else:
            failed.append((symbol, symbol))

    # Download ETFs
    print("\n" + "="*70)
    print("MAJOR ETFs")
    print("="*70)

    for symbol in OTHER_STOCKS:
        if download_ticker(symbol):
            successful += 1
        else:
            failed.append((symbol, symbol))

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed:     {len(failed)}")

    if failed:
        print("\nFailed downloads:")
        for symbol, name in failed:
            print(f"  - {symbol} ({name})")

    # Verify extreme events in key indices
    print("\n" + "="*70)
    print("EXTREME EVENTS VERIFICATION")
    print("="*70)

    verify_extreme_events("^GSPC", "SP500")
    verify_extreme_events("SPY", "SPY")

    # Final file listing
    print("\n" + "="*70)
    print("DOWNLOADED FILES")
    print("="*70)

    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    total_size = 0

    for csv_file in csv_files:
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  {csv_file.name:50s} {size_mb:6.2f} MB")

    print(f"\nTotal: {len(csv_files)} files, {total_size:.2f} MB")

    if failed:
        print(f"\n⚠ WARNING: {len(failed)} download(s) failed")
        return 1

    print(f"\n✓ All downloads complete!")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n✗ Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
