from __future__ import annotations

import io
import os
import re
import time
from datetime import date
from pathlib import Path
from typing import Iterable, Optional
from zipfile import ZipFile

import pandas as pd
import requests

BASE_URL = "https://www.histdata.com/get.php"
TOKEN_URL = "https://www.histdata.com/download-free-forex-data/?/ascii/1-minute-bar-quotes"
OUTPUT_DIR = Path("data/fx/raw")
PAIRS = ["EURUSD", "GBPUSD", "USDJPY"]
START_DATE = date(2010, 1, 1)
END_DATE = date(2024, 12, 31)
REQUEST_DELAY_SECONDS = 2.5
MAX_RETRIES = 3


def fetch_download_token(session: requests.Session) -> Optional[str]:
    """Fetch the HistData download token from the HTML page, if present."""
    response = session.get(TOKEN_URL, timeout=30)
    response.raise_for_status()
    match = re.search(r'name="tk"\s+value="([^"]+)"', response.text)
    if match:
        return match.group(1)
    return None


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


def build_form_data(pair: str, year: int, month: int, token: Optional[str]) -> dict[str, str]:
    """Build the form data required by HistData's download endpoint."""
    datemonth = f"{year}{month:02d}"
    data = {
        "date": str(year),
        "datemonth": datemonth,
        "platform": "ASCII",
        "timeframe": "M1",
        "fxpair": pair,
    }
    if token:
        data["tk"] = token
    return data


def request_zip_bytes(session: requests.Session, data: dict[str, str]) -> bytes:
    """Request a ZIP archive with retry handling."""
    last_error: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(BASE_URL, data=data, timeout=60)
            response.raise_for_status()
            if not response.content.startswith(b"PK"):
                raise ValueError("Response did not contain a ZIP archive.")
            return response.content
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            print(f"Attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            time.sleep(1 + attempt)
    raise RuntimeError(f"Failed to download data after {MAX_RETRIES} attempts.") from last_error


def parse_histdata_csv(csv_bytes: bytes) -> pd.DataFrame:
    """Parse HistData CSV bytes into the required schema."""
    df = pd.read_csv(io.BytesIO(csv_bytes), header=None)
    if df.shape[1] == 7:
        df.columns = ["date", "time", "open", "high", "low", "close", "volume"]
        date_str = df["date"].astype(str).str.zfill(8)
        time_str = df["time"].astype(str).str.zfill(6)
        dt = pd.to_datetime(
            date_str + time_str,
            format="%Y%m%d%H%M%S",
            errors="coerce",
        )
        df = df.assign(datetime=dt)
    elif df.shape[1] == 6:
        df.columns = ["datetime", "open", "high", "low", "close", "volume"]
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    else:
        raise ValueError(f"Unexpected CSV format with {df.shape[1]} columns.")
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


def download_fx_data() -> None:
    """Download 1-minute FX data from HistData and assemble yearly CSVs.

    The procedure downloads monthly ZIP archives from HistData, extracts the CSV,
    normalizes it to the schema (datetime, open, high, low, close, volume), and
    appends to a pair-level file in data/fx/raw. If the output file exists, the
    downloader resumes from the latest timestamp, avoiding duplicate rows.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total_months = len(list(month_iter(START_DATE, END_DATE)))

    with requests.Session() as session:
        token = fetch_download_token(session)
        if token:
            print("Download token found.")
        else:
            print("No download token found; continuing without it.")

        for pair in PAIRS:
            output_path = OUTPUT_DIR / f"{pair}_1min_2010_2024.csv"
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

                print(f"{pair}: downloading {year}-{month:02d}...")
                form_data = build_form_data(pair, year, month, token)
                zip_bytes = request_zip_bytes(session, form_data)
                zip_size = len(zip_bytes)

                csv_bytes = extract_first_csv(zip_bytes)
                csv_size = len(csv_bytes)
                df = parse_histdata_csv(csv_bytes)

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
    download_fx_data()


if __name__ == "__main__":
    main()
