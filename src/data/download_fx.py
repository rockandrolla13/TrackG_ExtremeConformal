from __future__ import annotations

import io
import lzma
import re
import struct
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

DUKASCOPY_BASE_URL = "https://datafeed.dukascopy.com/datafeed"
TRUEFX_DOWNLOADS_URL = "https://www.truefx.com/truefx-historical-downloads/"
OUTPUT_DIR = Path("data/fx/raw")
PAIRS = ("EURUSD", "GBPUSD", "USDJPY")
START_DATE = date(2010, 1, 1)
END_DATE = date(2024, 12, 31)
REQUEST_DELAY_SECONDS = 2.5
MAX_RETRIES = 3
REQUEST_TIMEOUT_SECONDS = 60
CSV_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]
PRICE_SCALES = {"EURUSD": 100_000, "GBPUSD": 100_000, "USDJPY": 1_000}


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


def hour_iter(start: datetime, end: datetime) -> Iterable[datetime]:
    """Yield hour-start datetimes from ``start`` to ``end`` inclusive."""
    current = start.replace(minute=0, second=0, microsecond=0)
    finish = end.replace(minute=0, second=0, microsecond=0)
    while current <= finish:
        yield current
        current += timedelta(hours=1)


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


def format_bytes(num_bytes: int) -> str:
    """Format a byte count for progress logging."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{num_bytes} B"


def is_pair_complete(last_timestamp: pd.Timestamp | None) -> bool:
    """Return whether the aggregate file already covers the requested range."""
    if last_timestamp is None:
        return False
    return last_timestamp >= pd.Timestamp(f"{END_DATE.isoformat()} 23:59:00")


def build_dukascopy_url(pair: str, hour_start: datetime) -> str:
    """Build the Dukascopy hourly tick URL for a pair and UTC hour."""
    return (
        f"{DUKASCOPY_BASE_URL}/{pair}/{hour_start.year}/{hour_start.month - 1:02d}/"
        f"{hour_start.day:02d}/{hour_start.hour:02d}h_ticks.bi5"
    )


def request_content(
    session: requests.Session,
    url: str,
    *,
    pair: str,
    label: str,
) -> bytes:
    """Download response bytes with retry-on-network-failure semantics."""
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response.content
        except requests.RequestException as exc:
            last_error = exc
            print(f"{pair} {label}: attempt {attempt}/{MAX_RETRIES} failed: {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(float(attempt))
    raise RuntimeError(f"Failed to download {pair} {label} after {MAX_RETRIES} attempts.") from last_error


def parse_dukascopy_bi5(compressed_bytes: bytes, pair: str, hour_start: datetime) -> pd.DataFrame:
    """Convert a Dukascopy hourly `.bi5` tick payload into normalized tick rows.

    Dukascopy exposes historical FX price feed data as hourly `.bi5` files under
    `datafeed.dukascopy.com`. Each record is 20 bytes: millisecond offset from
    the start of the hour, ask price integer, bid price integer, ask volume
    float, and bid volume float. Prices are converted using pair-specific pip
    scales; the script uses the mid price for OHLC and sums bid+ask sizes for a
    minute volume proxy before later aggregation.
    """
    raw_bytes = lzma.decompress(compressed_bytes)
    if not raw_bytes:
        return pd.DataFrame(columns=["datetime", "price", "volume"])
    if len(raw_bytes) % 20 != 0:
        raise ValueError(f"Unexpected Dukascopy payload length: {len(raw_bytes)} bytes.")

    rows: list[tuple[datetime, float, float]] = []
    price_scale = PRICE_SCALES[pair]
    for offset_ms, ask_raw, bid_raw, ask_volume, bid_volume in struct.iter_unpack(">IIIff", raw_bytes):
        timestamp = hour_start + timedelta(milliseconds=int(offset_ms))
        mid_price = ((bid_raw + ask_raw) / 2.0) / price_scale
        total_volume = float(ask_volume) + float(bid_volume)
        rows.append((timestamp, mid_price, total_volume))

    return pd.DataFrame(rows, columns=["datetime", "price", "volume"])


def aggregate_ticks_to_ohlcv(ticks: pd.DataFrame) -> pd.DataFrame:
    """Aggregate normalized tick rows into 1-minute OHLCV bars."""
    if ticks.empty:
        return pd.DataFrame(columns=CSV_COLUMNS)

    minute_ticks = ticks.copy()
    minute_ticks["datetime"] = pd.to_datetime(minute_ticks["datetime"]).dt.floor("min")
    grouped = minute_ticks.groupby("datetime", sort=True)
    bars = grouped.agg(
        open=("price", "first"),
        high=("price", "max"),
        low=("price", "min"),
        close=("price", "last"),
        volume=("volume", "sum"),
    )
    return bars.reset_index()[CSV_COLUMNS]


def append_to_output(output_path: Path, df: pd.DataFrame) -> None:
    """Append normalized rows to the aggregate pair CSV."""
    df.to_csv(output_path, mode="a", index=False, header=not output_path.exists())


def parse_truefx_csv(csv_bytes: bytes) -> pd.DataFrame:
    """Convert TrueFX tick CSV rows into 1-minute OHLCV bars.

    TrueFX historical downloads are documented as tick-level CSV files with
    instrument, timestamp, bid, and ask columns. When this fallback is used, the
    script computes the mid price and aggregates ticks into minute bars with the
    same output schema as the Dukascopy path.
    """
    df = pd.read_csv(io.BytesIO(csv_bytes), header=None)
    if df.shape[1] < 4:
        raise ValueError(f"Unexpected TrueFX CSV format with {df.shape[1]} columns.")

    df = df.iloc[:, :4].copy()
    df.columns = ["pair", "timestamp", "bid", "ask"]
    df["datetime"] = pd.to_datetime(df["timestamp"], format="%Y%m%d %H:%M:%S.%f", errors="coerce")
    df["price"] = (pd.to_numeric(df["bid"], errors="coerce") + pd.to_numeric(df["ask"], errors="coerce")) / 2.0
    df["volume"] = 0.0
    ticks = df[["datetime", "price", "volume"]].dropna(subset=["datetime", "price"])
    return aggregate_ticks_to_ohlcv(ticks)


def discover_truefx_month_url(page_html: str, pair: str, year: int, month: int) -> str | None:
    """Return a TrueFX ZIP URL for a month if the downloads page exposes one."""
    pattern = re.compile(
        rf'href="([^"]*{pair}[^"]*{year}[-_]?{month:02d}[^"]*\.zip)"',
        flags=re.IGNORECASE,
    )
    match = pattern.search(page_html)
    return match.group(1) if match else None


def download_truefx_pair(session: requests.Session, pair: str, output_path: Path) -> None:
    """Attempt a TrueFX fallback download using the public downloads page.

    The official downloads page may require a logged-in session. This function
    still makes a best-effort attempt: it fetches the page, looks for monthly ZIP
    links, downloads them when present, and aggregates the enclosed tick CSV into
    minute bars. If no direct links are exposed, it raises a clear error instead
    of silently succeeding.
    """
    listing_html = request_content(session, TRUEFX_DOWNLOADS_URL, pair=pair, label="truefx listing").decode(
        "utf-8",
        errors="ignore",
    )
    if "Please log in" in listing_html or "register for free access" in listing_html:
        raise RuntimeError("TrueFX historical downloads require an authenticated session.")

    bars_written = False
    last_timestamp = get_last_timestamp(output_path)
    for year, month in month_iter(START_DATE, END_DATE):
        month_url = discover_truefx_month_url(listing_html, pair, year, month)
        if month_url is None:
            raise RuntimeError(f"TrueFX did not expose a download link for {pair} {year}-{month:02d}.")

        if not month_url.startswith("http"):
            month_url = requests.compat.urljoin(TRUEFX_DOWNLOADS_URL, month_url)

        zip_bytes = request_content(session, month_url, pair=pair, label=f"TrueFX {year}-{month:02d}")
        csv_bytes = extract_first_csv(zip_bytes)
        df = parse_truefx_csv(csv_bytes)
        if last_timestamp is not None:
            df = df[df["datetime"] > last_timestamp]

        if not df.empty:
            append_to_output(output_path, df)
            last_timestamp = df["datetime"].iloc[-1]
            bars_written = True
            print(
                f"{pair}: TrueFX wrote {len(df):,} rows through {last_timestamp} "
                f"(zip {format_bytes(len(zip_bytes))}, csv {format_bytes(len(csv_bytes))})."
            )

        time.sleep(REQUEST_DELAY_SECONDS)

    if not bars_written:
        raise RuntimeError(f"TrueFX fallback produced no rows for {pair}.")


def extract_first_csv(zip_bytes: bytes) -> bytes:
    """Extract the first CSV member from a ZIP archive."""
    import zipfile

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
        names = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]
        if not names:
            raise ValueError("ZIP archive did not contain a CSV file.")
        with zip_ref.open(names[0]) as file_obj:
            return file_obj.read()


def download_pair_from_dukascopy(session: requests.Session, pair: str, output_path: Path) -> None:
    """Download and append all required hourly Dukascopy data for one pair."""
    last_timestamp = get_last_timestamp(output_path)
    if is_pair_complete(last_timestamp):
        print(f"{pair}: existing file already covers {START_DATE} to {END_DATE}, skipping.")
        return

    if last_timestamp is None:
        print(f"{pair}: starting Dukascopy download into {output_path}.")
        start_dt = datetime.combine(START_DATE, datetime.min.time())
    else:
        print(f"{pair}: resuming Dukascopy download after {last_timestamp} into {output_path}.")
        start_dt = last_timestamp.to_pydatetime().replace(minute=0, second=0, microsecond=0)

    end_dt = datetime.combine(END_DATE, datetime.max.time()).replace(minute=59, second=0, microsecond=0)
    hours = list(hour_iter(start_dt, end_dt))
    start_time = time.time()

    for index, hour_start in enumerate(hours, start=1):
        elapsed = time.time() - start_time
        average_seconds = elapsed / max(index - 1, 1) if index > 1 else 0.0
        remaining_seconds = average_seconds * (len(hours) - index + 1)
        label = hour_start.strftime("%Y-%m-%d %H:00")
        print(f"{pair}: [{index}/{len(hours)}] requesting Dukascopy {label} UTC (eta {remaining_seconds / 60:.1f} min).")

        bi5_bytes = request_content(session, build_dukascopy_url(pair, hour_start), pair=pair, label=label)
        ticks = parse_dukascopy_bi5(bi5_bytes, pair, hour_start)
        df = aggregate_ticks_to_ohlcv(ticks)

        if last_timestamp is not None:
            df = df[df["datetime"] > last_timestamp]

        if df.empty:
            print(f"{pair}: {label} produced no new bars (bi5 {format_bytes(len(bi5_bytes))}).")
        else:
            append_to_output(output_path, df)
            last_timestamp = df["datetime"].iloc[-1]
            output_size = output_path.stat().st_size
            print(
                f"{pair}: wrote {len(df):,} bars through {last_timestamp} "
                f"(bi5 {format_bytes(len(bi5_bytes))}, output {format_bytes(output_size)})."
            )

        if index < len(hours):
            time.sleep(REQUEST_DELAY_SECONDS)


def download_pair_data(session: requests.Session, pair: str) -> None:
    """Download a pair from Dukascopy first and fall back to TrueFX if needed."""
    output_path = OUTPUT_DIR / f"{pair}_1min_2010_2024.csv"
    try:
        download_pair_from_dukascopy(session, pair, output_path)
    except Exception as dukascopy_error:
        print(f"{pair}: Dukascopy download failed, trying TrueFX fallback: {dukascopy_error}")
        try:
            download_truefx_pair(session, pair, output_path)
        except Exception as truefx_error:
            raise RuntimeError(
                f"{pair}: Dukascopy failed ({dukascopy_error}); TrueFX fallback failed ({truefx_error})."
            ) from truefx_error


def download_fx_data() -> None:
    """Download aggregate 1-minute FX OHLCV files from Dukascopy.

    The primary source is Dukascopy's historical price feed, fetched from the
    official `datafeed.dukascopy.com` endpoint as hourly `.bi5` tick archives.
    Those ticks are decompressed, converted from Dukascopy's integer/float
    representation into timestamped prices and volumes, and aggregated into the
    required `datetime,open,high,low,close,volume` minute-bar schema.

    If Dukascopy is unavailable or blocks access, the script attempts a TrueFX
    fallback by discovering monthly ZIP links from the official downloads page
    and aggregating the fallback tick CSVs to the same 1-minute schema. Any
    unrecoverable error is raised so the command-line entrypoint exits with code
    `1` instead of reporting a false success.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        for pair in PAIRS:
            download_pair_data(session, pair)


def main() -> None:
    """Run the FX download job from the command line."""
    try:
        download_fx_data()
    except Exception as exc:
        print(f"FX download failed: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
