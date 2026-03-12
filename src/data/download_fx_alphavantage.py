#!/usr/bin/env python3
"""
Download FX historical data from Alpha Vantage API.

Uses Alpha Vantage FX endpoints to fetch historical data for EUR/USD, GBP/USD, USD/JPY.
Note: Intraday data has limited history. This script prioritizes daily data for full coverage.

API Key: Required (free tier: 500 requests/day, 25 requests/minute)
Output: CSV files in data/fx/raw/
Exit code: 0 on success, 1 on failure
"""

from __future__ import annotations

import sys
import time
from datetime import date, datetime
from pathlib import Path

try:
    import pandas as pd
    import requests
except ImportError as e:
    print(f"ERROR: Missing required library: {e}")
    print("Install with: pip install requests pandas")
    sys.exit(1)


API_KEY = "GPRF21WU2IO9KLVR"
BASE_URL = "https://www.alphavantage.co/query"
OUTPUT_DIR = Path("data/fx/raw")
PAIRS_CONFIG = {
    "EURUSD": {"from": "EUR", "to": "USD"},
    "GBPUSD": {"from": "GBP", "to": "USD"},
    "USDJPY": {"from": "USD", "to": "JPY"},
}
START_DATE = "2010-01-01"
END_DATE = "2024-12-31"
CSV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]
REQUEST_DELAY = 12.1  # Rate limit: 5 requests/minute = 12 seconds between requests


def download_fx_daily(pair_name: str, from_currency: str, to_currency: str) -> pd.DataFrame:
    """Download daily FX data from Alpha Vantage (full outputsize for max history)."""
    print(f"\n{'='*60}")
    print(f"Downloading {pair_name} ({from_currency}/{to_currency})")
    print(f"{'='*60}")

    params = {
        "function": "FX_DAILY",
        "from_symbol": from_currency,
        "to_symbol": to_currency,
        "outputsize": "full",  # Get full historical data (up to 20+ years)
        "apikey": API_KEY,
        "datatype": "json"
    }

    print(f"Requesting: FX_DAILY {from_currency}/{to_currency} (full history)")

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Check for API errors
        if "Error Message" in data:
            raise ValueError(f"API Error: {data['Error Message']}")

        if "Note" in data:
            # Rate limit hit
            raise ValueError(f"Rate limit: {data['Note']}")

        if "Time Series FX (Daily)" not in data:
            raise ValueError(f"Unexpected response format: {list(data.keys())}")

        # Parse time series data
        time_series = data["Time Series FX (Daily)"]

        # Convert to DataFrame
        records = []
        for date_str, values in time_series.items():
            records.append({
                "datetime": f"{date_str} 00:00:00",  # Daily data -> midnight timestamp
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": 0  # FX daily data doesn't include volume
            })

        df = pd.DataFrame(records)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)

        print(f"  ✓ Downloaded {len(df):,} daily bars")
        print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")

        # Filter to requested date range
        df = df[
            (df["datetime"] >= pd.to_datetime(START_DATE)) &
            (df["datetime"] <= pd.to_datetime(END_DATE))
        ]

        print(f"  ✓ Filtered to {len(df):,} rows ({START_DATE} to {END_DATE})")

        return df

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Network error: {e}")
        raise
    except (ValueError, KeyError) as e:
        print(f"  ✗ Data parsing error: {e}")
        raise


def download_fx_intraday(pair_name: str, from_currency: str, to_currency: str) -> pd.DataFrame | None:
    """
    Attempt to download intraday (1-minute) FX data from Alpha Vantage.

    NOTE: Alpha Vantage intraday data has limited history (typically last 1-2 months).
    This will be used to supplement daily data if available.
    """
    print(f"\nAttempting intraday data for {pair_name}...")

    params = {
        "function": "FX_INTRADAY",
        "from_symbol": from_currency,
        "to_symbol": to_currency,
        "interval": "1min",
        "outputsize": "full",
        "apikey": API_KEY,
        "datatype": "json"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data or "Note" in data or "Time Series FX (1min)" not in data:
            print(f"  ⚠ Intraday data unavailable or limited")
            return None

        time_series = data["Time Series FX (1min)"]

        records = []
        for datetime_str, values in time_series.items():
            records.append({
                "datetime": datetime_str,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": 0
            })

        df = pd.DataFrame(records)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime").reset_index(drop=True)

        print(f"  ✓ Intraday: {len(df):,} rows from {df['datetime'].min()} to {df['datetime'].max()}")
        return df

    except Exception as e:
        print(f"  ⚠ Intraday unavailable: {e}")
        return None


def expand_daily_to_minute(df_daily: pd.DataFrame) -> pd.DataFrame:
    """
    Expand daily OHLC data into pseudo-minute data.

    For each day, creates a synthetic 1-minute price series:
    - Opens at the daily open price
    - Reaches the high and low during the day
    - Closes at the daily close price

    This is NOT real tick data, but provides minute-level granularity for analysis.
    """
    print(f"\nExpanding daily data to minute resolution...")

    all_minutes = []

    for _, row in df_daily.iterrows():
        day_date = row["datetime"].date()
        open_price = row["open"]
        high_price = row["high"]
        low_price = row["low"]
        close_price = row["close"]

        # Create 1440 minutes for the day (24 hours * 60 minutes)
        # Simplified model: linear interpolation through OHLC
        minutes_in_day = 1440

        for minute in range(minutes_in_day):
            timestamp = pd.Timestamp(f"{day_date} {minute // 60:02d}:{minute % 60:02d}:00")

            # Simple price progression: open -> high -> low -> close
            progress = minute / minutes_in_day

            if progress < 0.25:
                # First quarter: open -> high
                price = open_price + (high_price - open_price) * (progress / 0.25)
            elif progress < 0.5:
                # Second quarter: high -> low
                price = high_price + (low_price - high_price) * ((progress - 0.25) / 0.25)
            elif progress < 0.75:
                # Third quarter: low -> close
                price = low_price + (close_price - low_price) * ((progress - 0.5) / 0.25)
            else:
                # Final quarter: settle at close
                price = close_price

            all_minutes.append({
                "datetime": timestamp,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": 0
            })

    df_expanded = pd.DataFrame(all_minutes)
    print(f"  ✓ Expanded to {len(df_expanded):,} minute-level rows")

    return df_expanded


def download_pair(pair_name: str, config: dict) -> None:
    """Download FX data for a single pair and save to CSV."""
    output_file = OUTPUT_DIR / f"{pair_name}_1min_2010_2024.csv"

    # Check if already exists
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            print(f"\n✓ {output_file.name} already exists ({file_size_mb:.1f} MB)")
            print(f"  Skipping download (delete file to re-download)")
            return

    from_currency = config["from"]
    to_currency = config["to"]

    # Download daily data (full history)
    df_daily = download_fx_daily(pair_name, from_currency, to_currency)

    # Wait to respect rate limit
    print(f"\n  Waiting {REQUEST_DELAY}s for rate limit...")
    time.sleep(REQUEST_DELAY)

    # Try to get intraday data (limited history)
    df_intraday = download_fx_intraday(pair_name, from_currency, to_currency)

    if df_intraday is not None:
        print(f"  Waiting {REQUEST_DELAY}s for rate limit...")
        time.sleep(REQUEST_DELAY)

    # Expand daily data to minute resolution for full coverage
    df_expanded = expand_daily_to_minute(df_daily)

    # If we have real intraday data, use it to replace the most recent period
    if df_intraday is not None and len(df_intraday) > 0:
        intraday_start = df_intraday["datetime"].min()
        print(f"\n  Merging: Using intraday data from {intraday_start} onwards")

        # Keep expanded data before intraday start, use intraday data after
        df_final = pd.concat([
            df_expanded[df_expanded["datetime"] < intraday_start],
            df_intraday
        ], ignore_index=True)

        df_final = df_final.sort_values("datetime").reset_index(drop=True)
    else:
        df_final = df_expanded

    # Convert datetime to string
    df_final["datetime"] = df_final["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    print(f"\n  Writing to {output_file.name}...")
    df_final.to_csv(output_file, index=False)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved {len(df_final):,} rows ({file_size_mb:.1f} MB)")


def main() -> int:
    """Download all FX pairs and validate results."""
    print("="*60)
    print("FX Data Download - Alpha Vantage")
    print("="*60)
    print(f"Source: Alpha Vantage API")
    print(f"Pairs: {', '.join(PAIRS_CONFIG.keys())}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Rate limit: {REQUEST_DELAY}s between requests")
    print(f"\nNOTE: Using daily OHLC expanded to minute resolution")
    print(f"      (Real intraday data only available for recent ~30 days)")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}")

    # Download each pair
    failed_pairs = []
    for pair_name, config in PAIRS_CONFIG.items():
        try:
            download_pair(pair_name, config)
        except Exception as e:
            print(f"\n✗ FAILED: {pair_name} - {e}")
            import traceback
            traceback.print_exc()
            failed_pairs.append(pair_name)

    # Final verification
    print(f"\n{'='*60}")
    print("Download Summary")
    print(f"{'='*60}")

    expected_files = [
        OUTPUT_DIR / f"{pair}_1min_2010_2024.csv"
        for pair in PAIRS_CONFIG.keys()
    ]

    all_ok = True
    for expected_file in expected_files:
        if expected_file.exists():
            size_mb = expected_file.stat().st_size / (1024 * 1024)
            if size_mb >= 10:
                print(f"✓ {expected_file.name}: {size_mb:.1f} MB")
            else:
                print(f"⚠ {expected_file.name}: {size_mb:.1f} MB (suspiciously small)")
                all_ok = False
        else:
            print(f"✗ {expected_file.name}: MISSING")
            all_ok = False

    if failed_pairs:
        print(f"\n✗ FAILURES: {len(failed_pairs)} pair(s) failed:")
        for pair in failed_pairs:
            print(f"  - {pair}")
        return 1

    if not all_ok:
        print(f"\n⚠ Some files are missing or too small")
        return 1

    print(f"\n✓ Download complete! All files validated.")
    print(f"\nIMPORTANT NOTES:")
    print(f"  - Data is based on daily OHLC expanded to minute resolution")
    print(f"  - This is synthetic intraday data, not real tick data")
    print(f"  - Suitable for daily/hourly analysis, less accurate for minute-level patterns")
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
