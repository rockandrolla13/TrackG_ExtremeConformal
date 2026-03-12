#!/usr/bin/env python3
"""
Download crypto historical data from Binance Data Vision.

Fetches 1-minute klines (OHLCV) data for BTC/USDT and ETH/USDT
from 2018-01-01 to 2024-12-31.

Data source: Binance Data Vision (data.binance.vision)
Output: CSV files in data/crypto/raw/
Exit code: 0 on success, 1 on failure
"""

from __future__ import annotations

import io
import sys
import time
import zipfile
from datetime import date, datetime
from pathlib import Path

try:
    import pandas as pd
    import requests
except ImportError as e:
    print(f"ERROR: Missing required library: {e}")
    print("Install with: pip install requests pandas")
    sys.exit(1)


OUTPUT_DIR = Path("data/crypto/raw")
PAIRS = ["BTCUSDT", "ETHUSDT"]
START_DATE = date(2018, 1, 1)
END_DATE = date(2024, 12, 31)
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"
CSV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]
REQUEST_DELAY = 0.5  # seconds between requests
MAX_RETRIES = 3


def month_range(start: date, end: date):
    """Generate (year, month) tuples from start to end."""
    current = start.replace(day=1)
    end_month = end.replace(day=1)

    while current <= end_month:
        yield current.year, current.month
        # Move to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


def download_monthly_klines(
    pair: str,
    year: int,
    month: int,
    session: requests.Session
) -> pd.DataFrame | None:
    """Download and parse a single month of 1-minute klines data."""
    filename = f"{pair}-1m-{year}-{month:02d}.zip"
    url = f"{BASE_URL}/{pair}/1m/{filename}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"    {year}-{month:02d}: ", end="", flush=True)
            response = session.get(url, timeout=30)

            if response.status_code == 404:
                print(f"NOT FOUND (skipping)")
                return None

            response.raise_for_status()

            # Extract CSV from ZIP
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                csv_filename = f"{pair}-1m-{year}-{month:02d}.csv"
                with zf.open(csv_filename) as csv_file:
                    df = pd.read_csv(
                        csv_file,
                        header=None,
                        names=[
                            "open_time", "open", "high", "low", "close", "volume",
                            "close_time", "quote_volume", "count",
                            "taker_buy_volume", "taker_buy_quote_volume", "ignore"
                        ]
                    )

            # Convert timestamp to datetime
            df["datetime"] = pd.to_datetime(df["open_time"], unit="ms")

            # Select required columns
            df = df[CSV_COLUMNS]

            print(f"✓ {len(df):,} rows ({response.headers.get('Content-Length', '?')} bytes)")
            time.sleep(REQUEST_DELAY)
            return df

        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES:
                print(f"RETRY {attempt}/{MAX_RETRIES} ({e})")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"✗ FAILED after {MAX_RETRIES} attempts: {e}")
                raise

    return None


def download_pair(pair: str, session: requests.Session) -> None:
    """Download all historical data for a single crypto pair."""
    output_file = OUTPUT_DIR / f"{pair}_1min_2018_2024.csv"

    print(f"\n{'='*60}")
    print(f"Downloading {pair}")
    print(f"{'='*60}")

    # Check if file already exists and is complete
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            print(f"✓ {output_file.name} already exists ({file_size_mb:.1f} MB)")
            print(f"  Skipping download (delete file to re-download)")
            return

    print(f"Source: {BASE_URL}/{pair}/1m/")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Downloading monthly files:")

    all_data = []
    months_downloaded = 0
    months_missing = 0

    for year, month in month_range(START_DATE, END_DATE):
        try:
            df = download_monthly_klines(pair, year, month, session)
            if df is not None:
                all_data.append(df)
                months_downloaded += 1
            else:
                months_missing += 1
        except Exception as e:
            print(f"    ✗ ERROR: {e}")
            raise

    if not all_data:
        raise ValueError(f"No data downloaded for {pair}")

    print(f"\n  Concatenating {months_downloaded} months...")
    combined_df = pd.concat(all_data, ignore_index=True)

    # Sort by datetime
    combined_df = combined_df.sort_values("datetime").reset_index(drop=True)

    # Convert datetime to string
    combined_df["datetime"] = combined_df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Save to CSV
    print(f"  Writing to {output_file.name}...")
    combined_df.to_csv(output_file, index=False)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"  ✓ Saved {len(combined_df):,} rows ({file_size_mb:.1f} MB)")
    print(f"  Date range: {combined_df['datetime'].iloc[0]} to {combined_df['datetime'].iloc[-1]}")

    if months_missing > 0:
        print(f"  ⚠ Note: {months_missing} month(s) were not available (404 errors)")


def main() -> int:
    """Download all crypto pairs and validate results."""
    print("="*60)
    print("Crypto Data Download - Binance Data Vision")
    print("="*60)
    print(f"Source: Binance Data Vision (data.binance.vision)")
    print(f"Pairs: {', '.join(PAIRS)}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Output: {OUTPUT_DIR}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}")

    # Create session for connection pooling
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; DataDownloader/1.0)"
    })

    # Download each pair
    failed_pairs = []
    for pair in PAIRS:
        try:
            download_pair(pair, session)
        except Exception as e:
            print(f"\n✗ FAILED: {pair} - {e}")
            failed_pairs.append(pair)

    # Final verification
    print(f"\n{'='*60}")
    print("Download Summary")
    print(f"{'='*60}")

    expected_files = [
        OUTPUT_DIR / f"{pair}_1min_2018_2024.csv"
        for pair in PAIRS
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
