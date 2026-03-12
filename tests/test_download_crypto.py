from __future__ import annotations

import io
from datetime import date
from zipfile import ZipFile

import pandas as pd

from src.data.download_crypto import (
    build_download_url,
    extract_first_csv,
    month_iter,
    parse_binance_csv,
)


def test_month_iter_inclusive() -> None:
    months = list(month_iter(date(2020, 12, 1), date(2021, 2, 1)))
    assert months == [(2020, 12), (2021, 1), (2021, 2)]


def test_build_download_url() -> None:
    url = build_download_url("BTCUSDT", 2024, 5)
    assert url.endswith("/BTCUSDT/1m/BTCUSDT-1m-2024-05.zip")


def test_parse_binance_csv_normalizes_schema() -> None:
    rows = [
        [1514764800000, 100.0, 110.0, 90.0, 105.0, 12.5, 0, 0, 0, 0, 0, 0],
        [1514764860000, 105.0, 112.0, 104.0, 110.0, 8.0, 0, 0, 0, 0, 0, 0],
    ]
    buffer = io.StringIO()
    pd.DataFrame(rows).to_csv(buffer, header=False, index=False)
    df = parse_binance_csv(buffer.getvalue().encode("utf-8"))
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert len(df) == 2
    assert df["datetime"].iloc[0].year == 2018


def test_extract_first_csv_returns_bytes() -> None:
    payload = b"1,2,3\n4,5,6\n"
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, "w") as zip_ref:
        zip_ref.writestr("sample.csv", payload)
    extracted = extract_first_csv(zip_buffer.getvalue())
    assert extracted == payload
