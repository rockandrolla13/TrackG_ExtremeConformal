from __future__ import annotations

import io
import time
from datetime import date
from pathlib import Path
from typing import Iterable
from zipfile import ZipFile

import pandas as pd
import requests

# Binance Data Vision is the top recommended crypto source from the research:
# free monthly spot kline ZIP archives, no API key required, and sufficient
# 1-minute history for BTCUSDT and ETHUSDT back to 2018.
BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"
OUTPUT_DIR = Path("data/crypto/raw")
PAIRS = ("BTCUSDT", "ETHUSDT")
START_DATE = date(2018, 1, 1)
END_DATE = date(2024, 12, 31)
REQUEST_DELAY_SECONDS = 2.5
MAX_RETRIES = 3
REQUEST_TIMEOUT_SECONDS = 60
CSV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]


def month_iter(start: date, end: date) -> Iterable[tuple[int, int]]:
    """Yield ``(year, month)`` tuples from ``start`` to ``end`` inclusive."""
    year = start.year
    month = start.month
    while (year, month) <= (end.year, end.month):
        yield year, month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1


def get_last_timestamp(output_path: Path) -> pd.Timestamp | None:
    """Return the last stored timestamp from an existing aggregate CSV."""
    if not output_path.exists():
        return None

    last_timestamp: pd.Timestamp | None = None
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
    """Build the monthly Binance Data Vision kline ZIP URL."""
    filename = f"{pair}-1m-{year}-{month:02d}.zip"
    return f"{BASE_URL}/{pair}/1m/{filename}"


def request_content(
    session: requests.Session,
    url: str,
    *,
    pair: str,
    label: str,
) -> bytes:
    """Download a monthly Binance ZIP archive with retry-on-network-failure."""
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            if not response.content.startswith(b"PK"):
                raise ValueError("response was not a ZIP archive")
            return response.content
        except (requests.RequestException, ValueError) as exc:
            last_error = exc
            print(f"{pair} {label}: attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(float(attempt))
    raise RuntimeError(
        f"Failed to download {pair} {label} after {MAX_RETRIES} attempts."
    ) from last_error


def extract_first_csv(zip_bytes: bytes) -> bytes:
    """Extract the first CSV file from a ZIP payload returned by Binance."""
    with ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
        names = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]
        if not names:
            raise ValueError("ZIP archive did not contain a CSV file.")
        with zip_ref.open(names[0]) as file_obj:
            return file_obj.read()


def parse_binance_csv(csv_bytes: bytes) -> pd.DataFrame:
    """Normalize Binance kline rows to ``datetime,open,high,low,close,volume``."""
    df = pd.read_csv(io.BytesIO(csv_bytes), header=None)
    if df.shape[1] < 6:
        raise ValueError(f"Unexpected CSV format with {df.shape[1]} columns.")

    df = df.iloc[:, :6].copy()
    df.columns = ["open_time", "open", "high", "low", "close", "volume"]
    dt = pd.to_datetime(df["open_time"], unit="ms", utc=True, errors="coerce")
    df = df.assign(datetime=dt.dt.tz_localize(None))

    normalized = df[CSV_COLUMNS].dropna(subset=["datetime"]).sort_values("datetime")
    return normalized.reset_index(drop=True)


def append_to_output(output_path: Path, df: pd.DataFrame) -> None:
    """Append normalized rows to the aggregate pair CSV."""
    df.to_csv(output_path, mode="a", index=False, header=not output_path.exists())


def format_bytes(num_bytes: int) -> str:
    """Format a byte count for progress logging."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{num_bytes} B"


def is_pair_complete(last_timestamp: pd.Timestamp | None) -> bool:
    """Return whether the aggregated file already covers the requested range."""
    if last_timestamp is None:
        return False
    return last_timestamp >= pd.Timestamp(f"{END_DATE.isoformat()} 23:59:00")


def download_pair_data(session: requests.Session, pair: str) -> None:
    """Download and append all required monthly files for one crypto pair."""
    output_path = OUTPUT_DIR / f"{pair}_1min_2018_2024.csv"
    last_timestamp = get_last_timestamp(output_path)
    if is_pair_complete(last_timestamp):
        print(f"{pair}: existing file already covers {START_DATE} to {END_DATE}, skipping.")
        return

    if last_timestamp is None:
        print(f"{pair}: starting fresh download into {output_path}.")
    else:
        print(f"{pair}: resuming after {last_timestamp} into {output_path}.")

    months = list(month_iter(START_DATE, END_DATE))
    pending_months = [
        (year, month)
        for year, month in months
        if last_timestamp is None or (year, month) >= (last_timestamp.year, last_timestamp.month)
    ]
    start_time = time.time()

    for index, (year, month) in enumerate(pending_months, start=1):
        elapsed = time.time() - start_time
        average_seconds = elapsed / max(index - 1, 1) if index > 1 else 0.0
        remaining_seconds = average_seconds * (len(pending_months) - index + 1)
        print(
            f"{pair}: [{index}/{len(pending_months)}] requesting {year}-{month:02d} "
            f"(eta {remaining_seconds / 60:.1f} min)."
        )

        label = f"{year}-{month:02d}"
        url = build_download_url(pair, year, month)
        zip_bytes = request_content(session, url, pair=pair, label=label)
        csv_bytes = extract_first_csv(zip_bytes)
        df = parse_binance_csv(csv_bytes)

        if last_timestamp is not None:
            df = df[df["datetime"] > last_timestamp]

        if df.empty:
            print(
                f"{pair}: {year}-{month:02d} contained no new rows "
                f"(zip {format_bytes(len(zip_bytes))}, csv {format_bytes(len(csv_bytes))})."
            )
        else:
            append_to_output(output_path, df)
            last_timestamp = df["datetime"].iloc[-1]
            output_size = output_path.stat().st_size
            print(
                f"{pair}: wrote {len(df):,} rows through {last_timestamp} "
                f"(zip {format_bytes(len(zip_bytes))}, csv {format_bytes(len(csv_bytes))}, "
                f"output {format_bytes(output_size)})."
            )

        if index < len(pending_months):
            print(f"{pair}: sleeping {REQUEST_DELAY_SECONDS:.1f}s before next request.")
            time.sleep(REQUEST_DELAY_SECONDS)


def download_crypto_data() -> None:
    """Download aggregate 1-minute crypto OHLCV files from Binance Data Vision.

    Binance Data Vision monthly spot kline ZIP archives were the top
    recommended crypto source from the research. This routine downloads each
    monthly archive, extracts and normalizes rows, and appends them into
    ``data/crypto/raw/{PAIR}_1min_2018_2024.csv``. Any unrecoverable failure
    raises so the CLI exits with status code 1.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        for pair in PAIRS:
            download_pair_data(session, pair)


def main() -> None:
    """Run the crypto download job from the command line."""
    try:
        download_crypto_data()
    except Exception as exc:
        print(f"Crypto download failed: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
