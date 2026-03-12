import pandas as pd

from src.data.download_fx import build_form_data, month_iter, parse_histdata_csv


def test_month_iter_inclusive():
    months = list(month_iter(pd.Timestamp("2010-01-01").date(), pd.Timestamp("2010-03-31").date()))
    assert months == [(2010, 1), (2010, 2), (2010, 3)]


def test_build_form_data_includes_token():
    data = build_form_data("EURUSD", 2012, 7, "token123")
    assert data["fxpair"] == "EURUSD"
    assert data["datemonth"] == "201207"
    assert data["tk"] == "token123"


def test_parse_histdata_csv_with_date_time_columns():
    csv_bytes = b"20100101,000000,1.1,1.2,1.0,1.15,123\n"
    df = parse_histdata_csv(csv_bytes)
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert df["datetime"].iloc[0] == pd.Timestamp("2010-01-01 00:00:00")
    assert df["close"].iloc[0] == 1.15


def test_parse_histdata_csv_with_datetime_column():
    csv_bytes = b"2010-01-01 00:00:00,1.1,1.2,1.0,1.15,123\n"
    df = parse_histdata_csv(csv_bytes)
    assert list(df.columns) == ["datetime", "open", "high", "low", "close", "volume"]
    assert df["datetime"].iloc[0] == pd.Timestamp("2010-01-01 00:00:00")
