# Crypto Historical Data

**Source:** Binance Data Vision (data.binance.vision)
**Download Date:** 2026-03-12
**Pairs:** BTCUSDT, ETHUSDT
**Date Range:** 2018-01-01 to 2024-12-31
**Frequency:** 1-minute klines (OHLCV)
**Timezone:** UTC
**File Format:** CSV (datetime,open,high,low,close,volume)

## Files
- BTCUSDT_1min_2018_2024.csv - missing; no file present in `data/crypto/raw` (`ls -lh data/crypto/raw` shows `total 0`)
- ETHUSDT_1min_2018_2024.csv - missing; no file present in `data/crypto/raw` (`ls -lh data/crypto/raw` shows `total 0`)

## Data Source Details
- Downloader: `src/data/download_crypto.py`
- Downloaded from Binance's official public data repository using monthly spot kline ZIP archives under `https://data.binance.vision/data/spot/monthly/klines/{PAIR}/1m/`.
- Intended aggregation: monthly kline files concatenated into single CSV outputs per pair at `data/crypto/raw/{PAIR}_1min_2018_2024.csv`.
- Download method: direct unauthenticated `GET` requests; no API key, cookies, or login required.
- Rate limiting / retries: up to `3` attempts per monthly archive, with `2.5` seconds between successful monthly requests.
- Actual execution result: the crypto stage was never started in Step 4 because the pipeline stopped immediately after the FX DNS failure.
- Missing months: all months remain missing because no crypto download requests were executed.

## Validation Summary
- Expected raw file count: `2`; actual count on 2026-03-12: `0`.
- Missing files: `BTCUSDT_1min_2018_2024.csv` and `ETHUSDT_1min_2018_2024.csv`.
- Step 4 (`.orch/steps/step_04_execute_downloads.md`): crypto downloads were not attempted because the workflow is fail-fast and FX failed first.
- Step 5 (`.orch/steps/step_05_validate_data_quality.md`): validation failed the prerequisite check because `data/crypto/raw/` contained no CSV files.

## Known Issues
- No local crypto dataset is present yet, so file sizes, row counts, missing-month checks, gap analysis, duplicate detection, and anomaly checks could not be measured.
- The UTC timezone reflects the downloader normalization logic in `src/data/download_crypto.py`, not a completed validation report over actual CSV outputs.
- Because the crypto stage never ran, the listed extreme-event coverage is expected coverage only.

## Extreme Events Captured
- 2020-03-12: COVID-19 crash
- 2021-05-19: May 2021 crash
- 2022-11-08: FTX collapse
