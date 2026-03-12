#!/usr/bin/env python3
"""
Download economic indicators from FRED (Federal Reserve Economic Data).

Downloads key economic indicators for context in extreme event analysis.
Includes: VIX, S&P 500, interest rates, yield curves, unemployment.

Source: Federal Reserve Bank of St. Louis (FRED)
API: Free with registration at https://fred.stlouisfed.org/docs/api/api_key.html
Output: CSV files in data/economic/raw/
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


OUTPUT_DIR = Path("data/economic/raw")
FRED_API_KEY = "YOUR_FRED_API_KEY_HERE"  # Get free at https://fred.stlouisfed.org/docs/api/api_key.html
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Economic indicators to download
FRED_SERIES = {
    # Volatility & Market Indices
    "VIXCLS": {
        "name": "VIX_Close",
        "description": "CBOE Volatility Index (VIX) - Market fear gauge",
        "start": "1990-01-02"
    },
    "SP500": {
        "name": "SP500_Index",
        "description": "S&P 500 Index",
        "start": "2010-01-01"
    },

    # Interest Rates
    "DFF": {
        "name": "Federal_Funds_Rate",
        "description": "Federal Funds Effective Rate (Daily)",
        "start": "2000-01-01"
    },
    "DGS10": {
        "name": "Treasury_10Y",
        "description": "10-Year Treasury Constant Maturity Rate",
        "start": "2000-01-01"
    },
    "DGS2": {
        "name": "Treasury_2Y",
        "description": "2-Year Treasury Constant Maturity Rate",
        "start": "2000-01-01"
    },

    # Yield Curve & Spreads
    "T10Y2Y": {
        "name": "Yield_Spread_10Y_2Y",
        "description": "10-Year minus 2-Year Treasury Spread (Recession indicator)",
        "start": "2000-01-01"
    },
    "T10Y3M": {
        "name": "Yield_Spread_10Y_3M",
        "description": "10-Year minus 3-Month Treasury Spread",
        "start": "2000-01-01"
    },

    # Economic Indicators
    "UNRATE": {
        "name": "Unemployment_Rate",
        "description": "Unemployment Rate (Monthly)",
        "start": "2000-01-01"
    },
    "CPIAUCSL": {
        "name": "CPI_All_Items",
        "description": "Consumer Price Index - Inflation (Monthly)",
        "start": "2000-01-01"
    },
    "GDP": {
        "name": "GDP",
        "description": "Gross Domestic Product (Quarterly)",
        "start": "2000-01-01"
    },

    # Credit Spreads
    "BAMLH0A0HYM2": {
        "name": "High_Yield_Spread",
        "description": "ICE BofA US High Yield Option-Adjusted Spread",
        "start": "2000-01-01"
    },
    "AAA": {
        "name": "AAA_Corporate",
        "description": "AAA Corporate Bond Yield",
        "start": "2000-01-01"
    },
}


def download_fred_series(series_id: str, config: dict) -> bool:
    """Download a single FRED time series."""
    name = config["name"]
    output_file = OUTPUT_DIR / f"{name}_daily.csv"

    # Check if already exists
    if output_file.exists():
        file_size_kb = output_file.stat().st_size / 1024
        if file_size_kb > 1:  # > 1KB
            print(f"  ✓ {name:30s} - already exists ({file_size_kb:.1f} KB)")
            return True

    if FRED_API_KEY == "YOUR_FRED_API_KEY_HERE":
        print(f"  ⚠ {name:30s} - FRED API key not configured")
        return False

    try:
        print(f"  ⬇ {name:30s} - downloading...", end=" ", flush=True)

        params = {
            'series_id': series_id,
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'observation_start': config['start']
        }

        response = requests.get(FRED_BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'observations' not in data:
            print(f"✗ UNEXPECTED FORMAT")
            return False

        observations = data['observations']

        # Filter out missing values and convert to DataFrame
        valid_obs = [obs for obs in observations if obs['value'] != '.']

        if not valid_obs:
            print(f"✗ NO DATA")
            return False

        df = pd.DataFrame(valid_obs)
        df['value'] = df['value'].astype(float)
        df['date'] = pd.to_datetime(df['date'])

        # Create standard format
        result_df = pd.DataFrame({
            'datetime': df['date'].dt.strftime('%Y-%m-%d'),
            'value': df['value'],
            'series_id': series_id,
            'series_name': name
        })

        # Save to CSV
        result_df.to_csv(output_file, index=False)

        file_size_kb = output_file.stat().st_size / 1024
        print(f"✓ {len(result_df):,} rows ({file_size_kb:.1f} KB)")

        return True

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP {e.response.status_code}")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def verify_key_events() -> None:
    """Verify that key economic events are visible in the data."""
    print("\n" + "="*70)
    print("KEY ECONOMIC EVENTS VERIFICATION")
    print("="*70)

    # Check VIX for major spikes
    vix_file = OUTPUT_DIR / "VIX_Close_daily.csv"
    if vix_file.exists():
        df = pd.read_csv(vix_file)
        df['datetime'] = pd.to_datetime(df['datetime'])

        print("\nVIX spikes during extreme events:")
        extreme_dates = [
            ("2008-09-29", "Lehman Brothers collapse"),
            ("2008-10-24", "2008 crisis peak VIX"),
            ("2010-05-06", "Flash Crash"),
            ("2015-08-24", "China crash"),
            ("2018-02-05", "VIXplosion"),
            ("2020-03-16", "COVID peak VIX"),
        ]

        for event_date, event_name in extreme_dates:
            event_dt = pd.to_datetime(event_date)
            if event_dt in df['datetime'].values:
                row = df[df['datetime'] == event_dt].iloc[0]
                print(f"  ✓ {event_date}: {event_name:30s} VIX = {row['value']:.2f}")
            else:
                print(f"  ⚠ {event_date}: {event_name:30s} NOT FOUND")

    # Check yield curve for inversions
    spread_file = OUTPUT_DIR / "Yield_Spread_10Y_2Y_daily.csv"
    if spread_file.exists():
        df = pd.read_csv(spread_file)
        df['datetime'] = pd.to_datetime(df['datetime'])

        print("\nYield curve inversions (10Y-2Y spread < 0):")
        inversions = df[df['value'] < 0]

        if len(inversions) > 0:
            # Group by year and show min spread per year
            inversions['year'] = pd.to_datetime(inversions['datetime']).dt.year
            yearly_min = inversions.groupby('year')['value'].min()

            for year, min_spread in yearly_min.items():
                print(f"  ⚠ {year}: Min spread = {min_spread:.3f}%")
        else:
            print("  ✓ No inversions in dataset period")

    # Check unemployment spikes
    unrate_file = OUTPUT_DIR / "Unemployment_Rate_daily.csv"
    if unrate_file.exists():
        df = pd.read_csv(unrate_file)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        print("\nUnemployment during crises:")
        crisis_dates = [
            ("2008-10-01", "2008 crisis"),
            ("2009-10-01", "2008 crisis peak unemployment"),
            ("2020-04-01", "COVID lockdowns"),
        ]

        for event_date, event_name in crisis_dates:
            event_dt = pd.to_datetime(event_date)
            # Find closest date (monthly data)
            closest_idx = (df['datetime'] - event_dt).abs().idxmin()
            row = df.loc[closest_idx]
            print(f"  ⚠ {row['datetime'].strftime('%Y-%m')}: {event_name:30s} UNRATE = {row['value']:.1f}%")


def main() -> int:
    """Download economic indicators from FRED."""
    print("="*70)
    print("Economic Indicators Download - FRED")
    print("="*70)
    print(f"Source: Federal Reserve Bank of St. Louis (FRED)")
    print(f"API: https://fred.stlouisfed.org/")
    print(f"Output: {OUTPUT_DIR}")

    # Check API key
    if FRED_API_KEY == "YOUR_FRED_API_KEY_HERE":
        print("\n" + "="*70)
        print("⚠ FRED API KEY NOT CONFIGURED")
        print("="*70)
        print("To download FRED data, you need a free API key:")
        print("1. Visit: https://fred.stlouisfed.org/")
        print("2. Create free account")
        print("3. Get API key: https://fred.stlouisfed.org/docs/api/api_key.html")
        print("4. Edit this script and replace YOUR_FRED_API_KEY_HERE")
        print("\nAlternative: Download manually from FRED website")
        print("="*70)
        return 1

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ Output directory ready: {OUTPUT_DIR}\n")

    # Download each series
    print("="*70)
    print("DOWNLOADING FRED SERIES")
    print("="*70)

    successful = 0
    failed = []

    for series_id, config in FRED_SERIES.items():
        if download_fred_series(series_id, config):
            successful += 1
        else:
            failed.append((series_id, config['name']))

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD SUMMARY")
    print("="*70)
    print(f"✓ Successful: {successful}")
    print(f"✗ Failed:     {len(failed)}")

    if failed:
        print("\nFailed downloads:")
        for series_id, name in failed:
            print(f"  - {series_id} ({name})")

    # Verify events
    if successful > 0:
        verify_key_events()

    # File listing
    print("\n" + "="*70)
    print("DOWNLOADED FILES")
    print("="*70)

    csv_files = sorted(OUTPUT_DIR.glob("*.csv"))
    total_size = 0

    for csv_file in csv_files:
        size_kb = csv_file.stat().st_size / 1024
        total_size += size_kb
        print(f"  {csv_file.name:40s} {size_kb:8.1f} KB")

    print(f"\nTotal: {len(csv_files)} files, {total_size:.1f} KB")

    if successful == 0:
        return 1

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
