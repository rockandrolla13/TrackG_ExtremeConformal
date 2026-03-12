#!/usr/bin/env python3
"""
Download VIX historical data from CBOE and FRED.

VIX (Volatility Index) is critical for extreme event research.
Covers major events: 2008 crisis, 2010 flash crash, 2020 COVID, etc.

Sources:
- CBOE: Official VIX provider (https://www.cboe.com/tradable-products/vix/)
- FRED: Federal Reserve Economic Data (https://fred.stlouisfed.org/series/VIXCLS)

Output: CSV file in data/indices/raw/
Exit code: 0 on success, 1 on failure
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    import requests
except ImportError as e:
    print(f"ERROR: Missing required library: {e}")
    print("Install with: pip install requests pandas")
    sys.exit(1)


OUTPUT_DIR = Path("data/indices/raw")
FRED_API_KEY = "YOUR_FRED_API_KEY"  # Get free key at https://fred.stlouisfed.org/docs/api/api_key.html
FRED_VIX_SERIES = "VIXCLS"  # VIX Close
CBOE_VIX_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv"


def download_from_cboe() -> pd.DataFrame | None:
    """Download VIX historical data directly from CBOE."""
    print("="*60)
    print("Downloading VIX from CBOE")
    print("="*60)
    print(f"URL: {CBOE_VIX_URL}")

    try:
        response = requests.get(CBOE_VIX_URL, timeout=30)
        response.raise_for_status()

        # Parse CSV
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))

        print(f"✓ Downloaded {len(df):,} rows from CBOE")
        print(f"  Date range: {df.iloc[0]['DATE']} to {df.iloc[-1]['DATE']}")

        # Rename columns to standard format
        df = df.rename(columns={
            'DATE': 'datetime',
            'OPEN': 'open',
            'HIGH': 'high',
            'LOW': 'low',
            'CLOSE': 'close'
        })

        # Add volume column (VIX doesn't have volume)
        df['volume'] = 0

        # Ensure datetime format
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d')

        # Select required columns
        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

        return df

    except Exception as e:
        print(f"✗ CBOE download failed: {e}")
        return None


def download_from_fred() -> pd.DataFrame | None:
    """Download VIX historical data from FRED (Federal Reserve)."""
    print("\n" + "="*60)
    print("Downloading VIX from FRED")
    print("="*60)

    if FRED_API_KEY == "YOUR_FRED_API_KEY":
        print("⚠ FRED API key not configured")
        print("  Get free key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("  Skipping FRED download")
        return None

    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            'series_id': FRED_VIX_SERIES,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'observation_start': '1990-01-01'
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'observations' not in data:
            raise ValueError(f"Unexpected FRED response: {data}")

        # Convert to DataFrame
        observations = data['observations']
        df = pd.DataFrame(observations)

        # Filter out missing values
        df = df[df['value'] != '.']
        df['value'] = df['value'].astype(float)

        # Create OHLCV format (FRED only provides close)
        df['datetime'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        df['close'] = df['value']
        df['open'] = df['close']  # Use close as approximation
        df['high'] = df['close']
        df['low'] = df['close']
        df['volume'] = 0

        df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

        print(f"✓ Downloaded {len(df):,} rows from FRED")
        print(f"  Date range: {df.iloc[0]['datetime']} to {df.iloc[-1]['datetime']}")

        return df

    except Exception as e:
        print(f"✗ FRED download failed: {e}")
        return None


def main() -> int:
    """Download VIX data and save to CSV."""
    print("="*60)
    print("VIX Historical Data Download")
    print("="*60)
    print(f"Output: {OUTPUT_DIR}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}")

    output_file = OUTPUT_DIR / "VIX_daily_1990_2026.csv"

    # Try CBOE first (no API key needed)
    df = download_from_cboe()

    # Fallback to FRED if CBOE fails
    if df is None:
        print("\n⚠ CBOE download failed, trying FRED...")
        df = download_from_fred()

    if df is None:
        print("\n✗ All download methods failed")
        return 1

    # Save to CSV
    print(f"\nWriting to {output_file.name}...")
    df.to_csv(output_file, index=False)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"✓ Saved {len(df):,} rows ({file_size_mb:.2f} MB)")

    # Show extreme events
    print("\n" + "="*60)
    print("Extreme Events Coverage")
    print("="*60)

    extreme_events = [
        ("2008-09-29", "Lehman Brothers / Financial Crisis"),
        ("2010-05-06", "Flash Crash"),
        ("2015-08-24", "China Market Crash"),
        ("2018-02-05", "VIXplosion / Volmageddon"),
        ("2020-03-16", "COVID-19 Crash (VIX peak)"),
    ]

    for event_date, event_name in extreme_events:
        if event_date in df['datetime'].values:
            row = df[df['datetime'] == event_date].iloc[0]
            print(f"✓ {event_date}: {event_name}")
            print(f"    VIX Close: {row['close']:.2f}")
        else:
            print(f"⚠ {event_date}: {event_name} - NOT FOUND")

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
