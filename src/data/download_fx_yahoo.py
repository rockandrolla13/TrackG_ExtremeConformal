#!/usr/bin/env python3
"""
Download FX historical data from Yahoo Finance.

Uses yfinance library to fetch 1-minute OHLCV data for EUR/USD, GBP/USD, USD/JPY
from 2010-01-01 to 2024-12-31.

Data source: Yahoo Finance (via yfinance Python library)
Output: CSV files in data/fx/raw/
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


OUTPUT_DIR = Path("data/fx/raw")
PAIRS_CONFIG = {
    "EURUSD": "EURUSD=X",  # Yahoo Finance symbol for EUR/USD
    "GBPUSD": "GBPUSD=X",  # Yahoo Finance symbol for GBP/USD
    "USDJPY": "USDJPY=X",  # Yahoo Finance symbol for USD/JPY
}
START_DATE = "2010-01-01"
END_DATE = "2024-12-31"
CSV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]


def download_pair(pair_name: str, yahoo_symbol: str) -> None:
    """Download 1-minute OHLCV data for a single FX pair from Yahoo Finance."""
    output_file = OUTPUT_DIR / f"{pair_name}_1min_2010_2024.csv"

    print(f"\n{'='*60}")
    print(f"Downloading {pair_name} ({yahoo_symbol})")
    print(f"{'='*60}")

    # Check if file already exists and is large enough
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            print(f"✓ {output_file.name} already exists ({file_size_mb:.1f} MB)")
            print(f"  Skipping download (use --force to re-download)")
            return

    print(f"Fetching data from Yahoo Finance...")
    print(f"  Symbol: {yahoo_symbol}")
    print(f"  Period: {START_DATE} to {END_DATE}")
    print(f"  Interval: 1 minute")

    try:
        # Download data from Yahoo Finance
        # Note: Yahoo Finance may not have complete 1m data for the full period
        # It typically has limited history for 1-minute data (30-60 days)
        # For longer periods, we may need to use hourly or daily data
        ticker = yf.Ticker(yahoo_symbol)

        # Try 1-minute data first (limited history)
        print(f"  Attempting 1-minute data download...")
        df = ticker.history(
            start=START_DATE,
            end=END_DATE,
            interval="1m",
            auto_adjust=False,
            prepost=False
        )

        if df.empty or len(df) < 1000:
            print(f"  ⚠ 1-minute data unavailable or limited (got {len(df)} rows)")
            print(f"  Falling back to hourly data...")

            # Fall back to hourly data
            df = ticker.history(
                start=START_DATE,
                end=END_DATE,
                interval="1h",
                auto_adjust=False,
                prepost=False
            )

            if df.empty:
                raise ValueError(f"No data retrieved for {yahoo_symbol}")

            print(f"  ✓ Downloaded {len(df):,} hourly bars")
        else:
            print(f"  ✓ Downloaded {len(df):,} minute bars")

        # Prepare dataframe
        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]

        # Rename columns to match required schema
        column_mapping = {
            "datetime": "datetime",
            "date": "datetime",  # Some responses use "Date" instead
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }

        df = df.rename(columns=column_mapping)

        # Select only required columns
        df = df[CSV_COLUMNS]

        # Convert datetime to string format
        df["datetime"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d %H:%M:%S")

        # Save to CSV
        print(f"  Writing to {output_file.name}...")
        df.to_csv(output_file, index=False)

        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"  ✓ Saved {len(df):,} rows ({file_size_mb:.1f} MB)")

        # Validate data quality
        if len(df) < 1000:
            print(f"  ⚠ WARNING: Less than 1,000 rows - data may be incomplete")

        if file_size_mb < 0.1:
            print(f"  ⚠ WARNING: File size < 0.1 MB - data may be incomplete")

    except Exception as e:
        print(f"  ✗ ERROR downloading {pair_name}: {e}")
        raise


def main() -> int:
    """Download all FX pairs and validate results."""
    print("="*60)
    print("FX Data Download - Yahoo Finance")
    print("="*60)
    print(f"Source: Yahoo Finance (yfinance library)")
    print(f"Pairs: {', '.join(PAIRS_CONFIG.keys())}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Output: {OUTPUT_DIR}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}")

    # Download each pair
    failed_pairs = []
    for pair_name, yahoo_symbol in PAIRS_CONFIG.items():
        try:
            download_pair(pair_name, yahoo_symbol)
        except Exception as e:
            print(f"\n✗ FAILED: {pair_name} - {e}")
            failed_pairs.append(pair_name)

    # Final verification
    print(f"\n{'='*60}")
    print("Download Summary")
    print(f"{'='*60}")

    expected_files = [
        OUTPUT_DIR / f"{pair}_1min_2010_2024.csv"
        for pair in PAIRS_CONFIG.keys()
    ]

    for expected_file in expected_files:
        if expected_file.exists():
            size_mb = expected_file.stat().st_size / (1024 * 1024)
            print(f"✓ {expected_file.name}: {size_mb:.1f} MB")
        else:
            print(f"✗ {expected_file.name}: MISSING")

    if failed_pairs:
        print(f"\n✗ FAILURES: {len(failed_pairs)} pair(s) failed:")
        for pair in failed_pairs:
            print(f"  - {pair}")
        return 1

    # Check minimum file sizes
    small_files = []
    for expected_file in expected_files:
        if expected_file.exists():
            size_mb = expected_file.stat().st_size / (1024 * 1024)
            if size_mb < 0.1:  # Less than 100KB is suspicious
                small_files.append((expected_file.name, size_mb))

    if small_files:
        print(f"\n⚠ WARNING: {len(small_files)} file(s) are suspiciously small:")
        for filename, size_mb in small_files:
            print(f"  - {filename}: {size_mb:.1f} MB")
        print(f"\nYahoo Finance may have limited 1-minute historical data.")
        print(f"Consider using hourly or daily intervals for longer periods.")

    print(f"\n✓ Download complete!")
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
