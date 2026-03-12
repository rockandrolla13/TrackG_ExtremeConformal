# FX Historical Data

**Source:** [HistData.com](https://www.histdata.com/download-free-forex-data/)
**Download Date:** 2026-03-12
**Pairs:** EUR/USD, GBP/USD, USD/JPY
**Date Range:** 2010-01-01 to 2024-12-31
**Frequency:** 1-minute OHLCV
**Timezone:** EST (GMT-5, per HistData source format; validator confirmation pending)
**File Format:** CSV (datetime,open,high,low,close,volume)

## Files
- EURUSD_1min_2010_2024.csv - missing; no file present in `data/fx/raw` (`ls -lh` shows `total 0`)
- GBPUSD_1min_2010_2024.csv - missing; no file present in `data/fx/raw` (`ls -lh` shows `total 0`)
- USDJPY_1min_2010_2024.csv - missing; no file present in `data/fx/raw` (`ls -lh` shows `total 0`)

## Data Source Details
- Downloader: `src/data/download_fx.py`
- Download method: `POST` form submission to `https://www.histdata.com/get.php` for monthly ASCII ZIP archives, after first loading HistData's public 1-minute download page.
- Authentication: no account credentials configured; the script extracts HistData's optional hidden `tk` anti-bot form token from the public page and submits it when available.
- Rate limiting / retries: the downloader sleeps `2.5` seconds between monthly requests, retries network or invalid-ZIP failures up to `3` times, and exits non-zero on unrecoverable failure.
- Actual execution result: Step 4 failed before any CSV was written because DNS resolution for `www.histdata.com` failed.

## Validation Summary
- Expected raw file count: `3`; actual count on 2026-03-12: `0`.
- Step 4 (`.orch/steps/step_04_execute_downloads.md`): FX download failed immediately with a DNS/name-resolution error, so no FX files were created.
- Step 5 (`.orch/steps/step_05_validate_data_quality.md`): validation failed the prerequisite check because `data/fx/raw/` contained no CSV files.

## Known Issues
- Missing files: `EURUSD_1min_2010_2024.csv`, `GBPUSD_1min_2010_2024.csv`, and `USDJPY_1min_2010_2024.csv`.
- Because no raw FX CSVs exist, there is no validated coverage, gap analysis, anomaly report, or measured file size to record yet.
- The displayed timezone is based on HistData's published format and the downloader assumptions, not on a completed local validation run.

## Extreme Events Captured
- 2015-01-15: SNB peg removal (Swiss franc)
- 2016-10-07: Brexit flash crash (Sterling)
- 2019-01-03: JPY flash crash
