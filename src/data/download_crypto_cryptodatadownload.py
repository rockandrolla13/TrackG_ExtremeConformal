#!/usr/bin/env python3
"""
Download cryptocurrency data from CryptoDataDownload.

Free daily OHLCV data from multiple exchanges since 2017.
Covers all major crypto extreme events.

NOTE: Minute-level data requires free registration at CryptoDataDownload.com.
      This script downloads daily data which is freely accessible without registration.
      For minute data, we use Binance Data Vision (see download_crypto_binance.py).

Source: CryptoDataDownload (https://www.cryptodatadownload.com/)
License: CC BY-NC-SA 4.0 (non-commercial use)
Output: CSV files in data/crypto/raw/
Exit code: 0 on success, 1 on failure
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from urllib.parse import quote

try:
    import pandas as pd
    import requests
except ImportError as e:
    print(f"ERROR: Missing required library: {e}")
    print("Install with: pip install requests pandas")
    sys.exit(1)


OUTPUT_DIR = Path("data/crypto/raw/cryptodatadownload")
BASE_URL = "https://www.cryptodatadownload.com/cdd"
REQUEST_DELAY = 2.0  # Be respectful to the server

# Priority pairs and exchanges
# Format: (exchange, pair, filename_suffix)
# NOTE: Using daily data (_d.csv) which is freely accessible
#       Minute data (_1m.csv) requires free registration
DOWNLOAD_CONFIG = [
    # Binance (most liquid)
    ("Binance", "BTCUSDT", "Binance_BTCUSDT_d.csv"),
    ("Binance", "ETHUSDT", "Binance_ETHUSDT_d.csv"),
    ("Binance", "BNBUSDT", "Binance_BNBUSDT_d.csv"),
    ("Binance", "ADAUSDT", "Binance_ADAUSDT_d.csv"),
    ("Binance", "SOLUSDT", "Binance_SOLUSDT_d.csv"),

    # Coinbase (BTC/USD direct)
    ("Coinbase", "BTCUSD", "Coinbase_BTCUSD_d.csv"),
    ("Coinbase", "ETHUSD", "Coinbase_ETHUSD_d.csv"),

    # Kraken (cross-validation)
    ("Kraken", "XBTUSD", "Kraken_XBTUSD_d.csv"),  # BTC
    ("Kraken", "ETHUSD", "Kraken_ETHUSD_d.csv"),

    # FTX (historical - for collapse study)
    ("FTX", "BTCUSD", "FTX_BTCUSD_d.csv"),
    ("FTX", "FTTUSD", "FTX_FTTUSD_d.csv"),  # FTX Token

    # Terra/Luna (for collapse study)
    ("Binance", "LUNAUSDT", "Binance_LUNAUSDT_d.csv"),
]


def construct_download_url(exchange: str, filename: str) -> str:
    """Construct CryptoDataDownload URL for a specific file."""
    # URL pattern: https://www.cryptodatadownload.com/cdd/{exchange}_{pair}_d.csv
    return f"{BASE_URL}/{filename}"


def download_pair(exchange: str, pair: str, filename: str) -> bool:
    """Download daily OHLCV data for a crypto pair."""
    output_file = OUTPUT_DIR / filename

    # Check if already exists
    if output_file.exists():
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 1.0:  # > 1MB
            print(f"  ✓ {exchange:12s} {pair:12s} - already exists ({file_size_mb:.1f} MB)")
            return True

    url = construct_download_url(exchange, filename)

    try:
        print(f"  ⬇ {exchange:12s} {pair:12s} - downloading...", end=" ", flush=True)

        response = requests.get(url, timeout=60)

        if response.status_code == 404:
            print(f"✗ NOT FOUND (404)")
            return False

        response.raise_for_status()

        # CryptoDataDownload CSVs have header rows, need to skip them
        # Typical format: first 2 lines are metadata, then column headers
        from io import StringIO
        content = response.text

        # Try to parse, skipping header lines
        try:
            df = pd.read_csv(StringIO(content), skiprows=1)
        except:
            # If that fails, try without skipping
            df = pd.read_csv(StringIO(content))

        if df.empty:
            print(f"✗ EMPTY FILE")
            return False

        # Save raw CSV
        output_file.write_text(content)

        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        print(f"✓ {len(df):,} rows ({file_size_mb:.1f} MB)")

        # Respectful delay
        time.sleep(REQUEST_DELAY)

        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"✗ NOT AVAILABLE")
        else:
            print(f"✗ HTTP {e.response.status_code}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def normalize_cryptodatadownload_csv(input_file: Path, output_file: Path) -> None:
    """
    Normalize CryptoDataDownload CSV to standard OHLCV format.

    CDD format varies by exchange but typically has:
    - Metadata in first 1-2 rows
    - Columns: unix, date, symbol, open, high, low, close, Volume {asset}, Volume {quote}
    """
    try:
        # Read with skiprows=1 to skip metadata
        df = pd.read_csv(input_file, skiprows=1)

        # Identify timestamp column (could be 'date', 'Date', 'timestamp', 'unix')
        timestamp_col = None
        for col in ['date', 'Date', 'timestamp', 'time']:
            if col in df.columns:
                timestamp_col = col
                break

        if timestamp_col is None and 'unix' in df.columns:
            # Convert unix timestamp to datetime
            df['datetime'] = pd.to_datetime(df['unix'], unit='s')
        elif timestamp_col:
            df['datetime'] = pd.to_datetime(df[timestamp_col])
        else:
            print(f"  ⚠ Could not find timestamp column in {input_file.name}")
            return

        # Standardize column names
        column_mapping = {
            'open': 'open',
            'Open': 'open',
            'high': 'high',
            'High': 'high',
            'low': 'low',
            'Low': 'low',
            'close': 'close',
            'Close': 'close',
        }

        df = df.rename(columns=column_mapping)

        # Find volume column (varies by exchange)
        volume_col = None
        for col in df.columns:
            if 'volume' in col.lower() and 'quote' not in col.lower():
                volume_col = col
                break

        if volume_col:
            df['volume'] = df[volume_col]
        else:
            df['volume'] = 0

        # Select standard columns
        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

        # Sort by datetime
        df = df.sort_values('datetime').reset_index(drop=True)

        # Convert datetime to string
        df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Save normalized version
        df.to_csv(output_file, index=False)

        print(f"    → Normalized to {output_file.name}")

    except Exception as e:
        print(f"  ⚠ Normalization failed: {e}")


def main() -> int:
    """Download crypto data from CryptoDataDownload."""
    print("="*70)
    print("Cryptocurrency Data Download - CryptoDataDownload")
    print("="*70)
    print(f"Source: CryptoDataDownload.com")
    print(f"License: CC BY-NC-SA 4.0 (Non-commercial)")
    print(f"Output: {OUTPUT_DIR}")
    print(f"\nNOTE: This downloads from a free community resource.")
    print(f"      Please be respectful and don't abuse the service.")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}\n")

    # Track results
    successful = 0
    failed = []

    # Download each pair
    print("="*70)
    print("DOWNLOADING CRYPTO PAIRS")
    print("="*70)

    for exchange, pair, filename in DOWNLOAD_CONFIG:
        if download_pair(exchange, pair, filename):
            successful += 1
        else:
            failed.append((exchange, pair, filename))

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed:     {len(failed)}")

    if failed:
        print("\nFailed downloads (may not be available):")
        for exchange, pair, filename in failed:
            print(f"  - {exchange} {pair}")

    # Normalize CSVs to standard format
    print("\n" + "="*70)
    print("NORMALIZING TO STANDARD FORMAT")
    print("="*70)

    raw_csvs = list(OUTPUT_DIR.glob("*.csv"))
    normalized_dir = OUTPUT_DIR.parent / "normalized"
    normalized_dir.mkdir(exist_ok=True)

    for csv_file in raw_csvs:
        if csv_file.stat().st_size > 1024:  # > 1KB
            output_file = normalized_dir / csv_file.name
            print(f"  {csv_file.name}")
            normalize_cryptodatadownload_csv(csv_file, output_file)

    # Final listing
    print("\n" + "="*70)
    print("DOWNLOADED FILES")
    print("="*70)

    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    total_size = 0

    for csv_file in csv_files:
        size_mb = csv_file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"  {csv_file.name:45s} {size_mb:8.1f} MB")

    print(f"\nTotal: {len(csv_files)} files, {total_size:.1f} MB")

    print("\n" + "="*70)
    print("IMPORTANT NOTES")
    print("="*70)
    print("• Data license: CC BY-NC-SA 4.0 (Non-commercial use only)")
    print("• Raw files: data/crypto/raw/cryptodatadownload/")
    print("• Normalized: data/crypto/raw/normalized/")
    print("• Some pairs may not be available (404 errors are normal)")
    print("• FTX historical data may no longer be available")

    if successful == 0:
        print("\n✗ No files downloaded successfully")
        return 1

    print(f"\n✓ Download complete! {successful} file(s) downloaded.")
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
