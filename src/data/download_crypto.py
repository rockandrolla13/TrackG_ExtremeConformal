from __future__ import annotations

import io
import time
from datetime import date
from pathlib import Path
from typing import Iterable, Optional
from zipfile import ZipFile

import pandas as pd
import requests

# Binance provides free, unauthenticated 1-minute spot data dumps with history
# back to 2017+, which is the longest public history available without API keys.
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"
OUTPUT_DIR = Path("data/crypto/raw")
PAIRS = ["BTCUSDT", "ETHUSDT"]
START_DATE = date(2018, 1, 1)
END_DATE = date(2024, 12, 31)
REQUEST_DELAY_SECONDS = 2.5
MAX_RETRIES = 3


def month_iter(start: date, end: date) -> Iterable[tuple[int, int]]:
    """Yield (year, month) tuples from start to end inclusive."""
    year = start.year
    month = start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


def get_last_timestamp(output_path: Path) -> Optional[pd.Timestamp]:
    """Read the last datetime from an existing output file for resume support."""
    if not output_path.exists():
        return None
    last_timestamp: Optional[pd.Timestamp] = None
    for chunk in pd.read_csv(
        output_path,
        usecols=["datetime"],
        parse_dates=["datetime"],
        chunksize=500_000,
    ):
        if not chunk.empty:
            last_timestamp = chunk["datetime"].iloc[-1]
    return last_timestamp


def build_download_url(pair: str, year: int, month: int) -> str:
    """Build the Binance monthly ZIP URL for a symbol and month."""
    filename = f"{pair}-1m-{year}-{month:02d}.zip"
    return f"{BASE_URL}/{pair}/1m/{filename}"


def request_zip_bytes(session: requests.Session, url: str) -> bytes:
    """Request a ZIP archive with retry handling."""
    last_error: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=60)
            response.raise_for_status()
            if not response.content.startswith(b"PK"):
                raise ValueError("Response did not contain a ZIP archive.")
            return response.content
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            time.sleep(1 + attempt)
    raise RuntimeError(f"Failed to download data after {MAX_RETRIES} attempts.") from last_error


def parse_binance_csv(csv_bytes: bytes) -> pd.DataFrame:
    """Parse Binance CSV bytes into the required schema."""
    df = pd.read_csv(io.BytesIO(csv_bytes), header=None)
    if df.shape[1] < 6:
        raise ValueError(f"Unexpected CSV format with {df.shape[1]} columns.")
    df = df.iloc[:, :6]
    df.columns = ["open_time", "open", "high", "low", "close", "volume"]
    dt = pd.to_datetime(df["open_time"], unit="ms", utc=True, errors="coerce")
    df = df.assign(datetime=dt.dt.tz_localize(None))
    df = df[["datetime", "open", "high", "low", "close", "volume"]]
    df = df.dropna(subset=["datetime"])
    return df


def extract_first_csv(zip_bytes: bytes) -> bytes:
    """Extract the first CSV file from a ZIP archive."""
    with ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
        names = zip_ref.namelist()
        if not names:
            raise ValueError("ZIP archive was empty.")
        with zip_ref.open(names[0]) as file_obj:
            return file_obj.read()


def append_to_output(output_path: Path, df: pd.DataFrame) -> None:
    """Append data to the output file with the required schema."""
    header = not output_path.exists()
    df.to_csv(output_path, mode="a", index=False, header=header)


def download_crypto_data() -> None:
    """Download 1-minute crypto data and assemble yearly CSVs.

    The procedure downloads monthly ZIP archives from Binance data dumps,
    extracts the CSV, normalizes it to the schema (datetime, open, high, low,
    close, volume), and appends to a pair-level file in data/crypto/raw. If the
    output file exists, the downloader resumes from the latest timestamp,
    avoiding duplicate rows.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total_months = len(list(month_iter(START_DATE, END_DATE)))

    with requests.Session() as session:
        for pair in PAIRS:
            output_path = OUTPUT_DIR / f"{pair}_1min_2018_2024.csv"
            last_timestamp = get_last_timestamp(output_path)
            if last_timestamp:
                print(f"{pair}: resuming after {last_timestamp}.")
            else:
                print(f"{pair}: starting fresh download.")

            completed_months = 0
            start_time = time.time()

            for year, month in month_iter(START_DATE, END_DATE):
                if last_timestamp and (year, month) < (last_timestamp.year, last_timestamp.month):
                    continue

                url = build_download_url(pair, year, month)
                print(f"{pair}: downloading {year}-{month:02d}...")
                zip_bytes = request_zip_bytes(session, url)
                zip_size = len(zip_bytes)

                csv_bytes = extract_first_csv(zip_bytes)
                csv_size = len(csv_bytes)
                df = parse_binance_csv(csv_bytes)

                if last_timestamp:
                    df = df[df["datetime"] > last_timestamp]

                if not df.empty:
                    append_to_output(output_path, df)
                    output_size = output_path.stat().st_size
                    print(
                        f"{pair}: wrote {len(df)} rows, zip {zip_size} bytes, "
                        f"csv {csv_size} bytes, output {output_size} bytes."
                    )
                else:
                    print(f"{pair}: no new rows for {year}-{month:02d}.")

                completed_months += 1
                elapsed = time.time() - start_time
                avg_per_month = elapsed / max(completed_months, 1)
                remaining = total_months - completed_months
                eta_seconds = remaining * avg_per_month
                print(f"{pair}: ETA {eta_seconds / 60:.1f} minutes.")

                time.sleep(REQUEST_DELAY_SECONDS)


def main() -> None:
    """CLI entry point."""
    download_crypto_data()


if __name__ == "__main__":
    main()
