from __future__ import annotations

import io
import lzma
import struct
from datetime import date, datetime
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from src.data.download_fx import (
    aggregate_ticks_to_ohlcv,
    build_dukascopy_url,
    discover_truefx_month_url,
    extract_first_csv,
    format_bytes,
    get_last_timestamp,
    is_pair_complete,
    month_iter,
    parse_dukascopy_bi5,
    parse_truefx_csv,
)


def test_month_iter_inclusive() -> None:
    months = list(month_iter(date(2010, 1, 1), date(2010, 3, 31)))
    assert months == [(2010, 1), (2010, 2), (2010, 3)]


def test_build_dukascopy_url_uses_zero_based_month() -> None:
    url = build_dukascopy_url("EURUSD", datetime(2010, 1, 2, 3, 0, 0))
    assert url.endswith("/EURUSD/2010/00/02/03h_ticks.bi5")


def test_parse_dukascopy_bi5_normalizes_ticks() -> None:
    payload = struct.pack(
        ">IIIffIIIff",
        0,
        110020,
        110000,
        1.0,
        2.0,
        30_000,
        110040,
        110020,
        3.0,
        4.0,
    )
    df = parse_dukascopy_bi5(lzma.compress(payload), "EURUSD", datetime(2010, 1, 1, 0, 0, 0))
    assert list(df.columns) == ["datetime", "price", "volume"]
    assert df["datetime"].iloc[1] == pd.Timestamp("2010-01-01 00:00:30")
    assert df["price"].iloc[0] == 1.1001
    assert df["volume"].iloc[1] == 7.0


def test_aggregate_ticks_to_ohlcv_builds_minute_bars() -> None:
    ticks = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                [
                    "2010-01-01 00:00:01",
                    "2010-01-01 00:00:20",
                    "2010-01-01 00:00:50",
                    "2010-01-01 00:01:10",
                ]
            ),
            "price": [1.1, 1.2, 1.15, 1.3],
            "volume": [1.0, 2.0, 3.0, 4.0],
        }
    )
    df = aggregate_ticks_to_ohlcv(ticks)
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert df.iloc[0].to_dict() == {
        "datetime": pd.Timestamp("2010-01-01 00:00:00"),
        "open": 1.1,
        "high": 1.2,
        "low": 1.1,
        "close": 1.15,
        "volume": 6.0,
    }


def test_parse_truefx_csv_aggregates_mid_prices() -> None:
    csv_bytes = (
        b"EUR/USD,20100101 00:00:00.000,1.1000,1.1002\n"
        b"EUR/USD,20100101 00:00:30.000,1.1010,1.1012\n"
    )
    df = parse_truefx_csv(csv_bytes)
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert df["datetime"].iloc[0] == pd.Timestamp("2010-01-01 00:00:00")
    assert df["open"].iloc[0] == 1.1001
    assert df["close"].iloc[0] == 1.1011


def test_discover_truefx_month_url_returns_matching_zip() -> None:
    html = '<a href="/downloads/EURUSD-2010-01.zip">EURUSD Jan 2010</a>'
    assert discover_truefx_month_url(html, "EURUSD", 2010, 1) == "/downloads/EURUSD-2010-01.zip"


def test_extract_first_csv_returns_csv_member() -> None:
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_ref:
        zip_ref.writestr("README.txt", b"ignored")
        zip_ref.writestr("sample.csv", b"a,b,c\n1,2,3\n")
    assert extract_first_csv(zip_buffer.getvalue()) == b"a,b,c\n1,2,3\n"


def test_format_bytes_uses_human_readable_units() -> None:
    assert format_bytes(512) == "512.0 B"
    assert format_bytes(2048) == "2.0 KB"


def test_get_last_timestamp_reads_existing_output(tmp_path: Path) -> None:
    output_path = tmp_path / "EURUSD_1min_2010_2024.csv"
    pd.DataFrame(
        [
            {"datetime": "2010-01-01 00:00:00", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1},
            {"datetime": "2024-12-31 23:59:00", "open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1},
        ]
    ).to_csv(output_path, index=False)
    assert get_last_timestamp(output_path) == pd.Timestamp("2024-12-31 23:59:00")


def test_is_pair_complete_requires_end_of_range() -> None:
    assert is_pair_complete(pd.Timestamp("2024-12-31 23:59:00")) is True
    assert is_pair_complete(pd.Timestamp("2024-12-31 23:58:00")) is False
    assert is_pair_complete(None) is False
