# FX Historical Data

**Source:** Dukascopy Swiss Bank (primary) with TrueFX fallback
**Download Date:** 2026-03-12
**Pairs:** EUR/USD, GBP/USD, USD/JPY
**Date Range:** 2010-01-01 to 2024-12-31
**Frequency:** 1-minute OHLCV
**Timezone:** UTC for the Dukascopy path; validation could not confirm because no CSVs were created
**File Format:** CSV (datetime,open,high,low,close,volume)

## Files
- EURUSD_1min_2010_2024.csv - missing; no file present in `data/fx/raw` (`ls -lh data/fx/raw` shows `total 0`)
- GBPUSD_1min_2010_2024.csv - missing; no file present in `data/fx/raw` (`ls -lh data/fx/raw` shows `total 0`)
- USDJPY_1min_2010_2024.csv - missing; no file present in `data/fx/raw` (`ls -lh data/fx/raw` shows `total 0`)

## Data Source Details
- Downloader: `src/data/download_fx.py`
- Primary source: Dukascopy historical feed at `https://datafeed.dukascopy.com/datafeed`, downloaded as hourly `.bi5` tick archives and aggregated locally into 1-minute OHLCV bars.
- Fallback source: TrueFX historical downloads page at `https://www.truefx.com/truefx-historical-downloads/`, intended to discover monthly ZIP files and aggregate tick CSVs into the same output schema if Dukascopy fails.
- Download method: direct `GET` requests with retry logic; the script attempts Dukascopy first for each pair and only falls back to TrueFX if the Dukascopy path raises an error.
- Authentication: no credentials were configured; the TrueFX fallback would only work if the public downloads page exposed downloadable links without login.
- Rate limiting / retries: up to `3` attempts per request, with backoff on request failures and `2.5` seconds between successful hourly/monthly fetches.
- Actual execution result: Step 4 failed on the first FX pair because DNS resolution failed for both `datafeed.dukascopy.com` and `www.truefx.com`, so no CSV files were written.

## Validation Summary
- Expected raw file count: `3`; actual count on 2026-03-12: `0`.
- Missing files: `EURUSD_1min_2010_2024.csv`, `GBPUSD_1min_2010_2024.csv`, and `USDJPY_1min_2010_2024.csv`.
- Step 4 (`.orch/steps/step_04_execute_downloads.md`): the FX stage failed fast on network/DNS errors before producing any output.
- Step 5 (`.orch/steps/step_05_validate_data_quality.md`): validation failed the prerequisite check because `data/fx/raw/` contained no CSV files.

## Known Issues
- No local FX dataset is present yet, so file sizes, row counts, date coverage, gaps, duplicates, and anomaly checks could not be measured.
- The documented timezone is inferred from the downloader implementation, which labels Dukascopy requests as UTC hours; there is no completed validation run to confirm downstream CSV timestamps.
- Because the FX stage failed, the intended extreme-event coverage is theoretical until the download is rerun successfully.

## Extreme Events Captured
- 2015-01-15: SNB peg removal (Swiss franc)
- 2016-10-07: Brexit flash crash (Sterling)
- 2019-01-03: JPY flash crash
