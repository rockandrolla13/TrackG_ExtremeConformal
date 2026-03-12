# Crypto Historical Data

**Source:** [Binance Data Vision](https://data.binance.vision/) for Binance spot market klines
**Download Date:** 2026-03-12
**Pairs:** BTC/USDT, ETH/USDT
**Date Range:** 2018-01-01 to 2024-12-31
**Frequency:** 1-minute OHLCV
**Timezone:** UTC (normalization implemented in downloader; validator confirmation pending)
**File Format:** CSV (datetime,open,high,low,close,volume)

## Files
- BTCUSDT_1min_2018_2024.csv - missing; no file present in `data/crypto/raw` (`ls -lh` shows `total 0`)
- ETHUSDT_1min_2018_2024.csv - missing; no file present in `data/crypto/raw` (`ls -lh` shows `total 0`)

## Data Source Details
- Downloader: `src/data/download_crypto.py`
- Exchange / source: Binance spot 1-minute monthly kline ZIP archives served from Binance Data Vision.
- Download method: direct `GET` requests to `https://data.binance.vision/data/spot/monthly/klines/{PAIR}/1m/{PAIR}-1m-YYYY-MM.zip`.
- Authentication: no API key, cookies, or login required.
- Rate limiting / retries: the downloader sleeps `2.5` seconds between monthly requests, retries network or invalid-ZIP failures up to `3` times, and exits non-zero on unrecoverable failure.
- Actual execution result: the crypto stage was not started in Step 4 because the pipeline stopped after the FX DNS failure.

## Validation Summary
- Expected raw file count: `2`; actual count on 2026-03-12: `0`.
- Step 4 (`.orch/steps/step_04_execute_downloads.md`): crypto downloads were not attempted because the pipeline failed fast on FX.
- Step 5 (`.orch/steps/step_05_validate_data_quality.md`): validation failed the prerequisite check because `data/crypto/raw/` contained no CSV files.

## Known Issues
- Missing files: `BTCUSDT_1min_2018_2024.csv` and `ETHUSDT_1min_2018_2024.csv`.
- Because no raw crypto CSVs exist, there is no validated coverage, gap analysis, anomaly report, or measured file size to record yet.
- The documented UTC timezone reflects downloader normalization logic, not a completed local validation run.

## Extreme Events Captured
- 2020-03-12: COVID-19 market crash
- 2021-05-19: May 2021 crypto crash (China mining ban)
- 2022-11-08: FTX collapse and contagion
