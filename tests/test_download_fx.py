from __future__ import annotations

import io
from datetime import date
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from src.data.download_fx import (
    build_form_data,
    extract_first_csv,
    format_bytes,
    get_last_timestamp,
    is_pair_complete,
    month_iter,
    parse_histdata_csv,
)


def test_month_iter_inclusive() -> None:
    months = list(month_iter(date(2010, 1, 1), date(2010, 3, 31)))
    assert months == [(2010, 1), (2010, 2), (2010, 3)]


def test_build_form_data_includes_token() -> None:
    data = build_form_data("EURUSD", 2012, 7, "token123")
    assert data["fxpair"] == "EURUSD"
    assert data["datemonth"] == "201207"
    assert data["tk"] == "token123"


def test_parse_histdata_csv_with_date_time_columns() -> None:
    csv_bytes = b"20100101,000000,1.1,1.2,1.0,1.15,123\n"
    df = parse_histdata_csv(csv_bytes)
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert df["datetime"].iloc[0] == pd.Timestamp("2010-01-01 00:00:00")
    assert df["close"].iloc[0] == 1.15


def test_parse_histdata_csv_with_datetime_column() -> None:
    csv_bytes = b"2010-01-01 00:00:00,1.1,1.2,1.0,1.15,123\n"
    df = parse_histdata_csv(csv_bytes)
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert df["datetime"].iloc[0] == pd.Timestamp("2010-01-01 00:00:00")


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
