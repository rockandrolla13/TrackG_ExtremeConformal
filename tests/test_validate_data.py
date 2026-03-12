from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from src.data.validate_data import (
    analyze_file,
    check_date_bounds,
    describe_date_gaps,
    find_missing_extreme_dates,
    has_required_csv_inputs,
    infer_timezone,
)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def test_describe_date_gaps_weekend_allowed() -> None:
    dates = [date(2024, 1, 5), date(2024, 1, 8)]
    assert describe_date_gaps(dates, allow_weekends=True) == []
    assert describe_date_gaps(dates, allow_weekends=False) == ["2024-01-05 -> 2024-01-08 (3 days)"]


def test_find_missing_extreme_dates() -> None:
    dates = [date(2020, 3, 12), date(2021, 5, 19)]
    required = {date(2020, 3, 12), date(2022, 11, 8)}
    assert find_missing_extreme_dates(dates, required) == [date(2022, 11, 8)]


def test_infer_timezone_utc() -> None:
    min_times = {date(2024, 1, 1): 0, date(2024, 1, 2): 60}
    assert infer_timezone(min_times).startswith("UTC")


def test_check_date_bounds() -> None:
    passed, failures = check_date_bounds(date(2018, 1, 1), date(2024, 12, 31), date(2018, 1, 1))
    assert passed is True
    assert failures == []

    passed, failures = check_date_bounds(None, None, date(2018, 1, 1))
    assert passed is False
    assert "missing start date" in failures
    assert "missing end date" in failures


def test_analyze_file_quality(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    write_csv(
        path,
        [
            {
                "datetime": "2010-01-01 00:00:00",
                "open": 1.0,
                "high": 1.2,
                "low": 0.9,
                "close": 1.1,
                "volume": 0,
            },
            {
                "datetime": "2010-01-02 00:01:00",
                "open": -1.0,
                "high": 0.5,
                "low": 0.4,
                "close": 0.6,
                "volume": 0,
            },
        ],
    )

    stats = analyze_file(path)
    assert stats.start_date == date(2010, 1, 1)
    assert stats.end_date == date(2010, 1, 2)
    assert stats.date_set == {date(2010, 1, 1), date(2010, 1, 2)}
    assert stats.negative_price_rows == 1
    assert stats.bad_close_range_rows == 1
    assert stats.nonzero_volume_seen is False


def test_has_required_csv_inputs_requires_both_directories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fx_dir = tmp_path / "fx"
    crypto_dir = tmp_path / "crypto"
    fx_dir.mkdir()
    crypto_dir.mkdir()
    write_csv(
        fx_dir / "eurusd.csv",
        [
            {
                "datetime": "2010-01-01 00:00:00",
                "open": 1.0,
                "high": 1.1,
                "low": 0.9,
                "close": 1.0,
                "volume": 1,
            }
        ],
    )

    monkeypatch.setattr("src.data.validate_data.FX_DIR", fx_dir)
    monkeypatch.setattr("src.data.validate_data.CRYPTO_DIR", crypto_dir)

    ok, message = has_required_csv_inputs()
    assert ok is False
    assert message == "ERROR: No CSV files found. Downloads must have failed."
