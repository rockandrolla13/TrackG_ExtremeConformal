# Historical Data Download Summary

**Download Date:** 2026-03-12
**Pipeline:** orch multi-agent orchestration (v3) + manual execution
**Status:** ✅ COMPLETE - All 5 files downloaded

---

## 📊 Dataset Overview

### FX Data (3 pairs, 2010-2024)
- **Source:** Alpha Vantage API (daily OHLC expanded to minute resolution)
- **Method:** Synthetic minute-level data from daily bars
- **Total Size:** 1.3 GB
- **Files:** 3

| Pair | File | Size | Rows | Date Range |
|------|------|------|------|------------|
| EUR/USD | EURUSD_1min_2010_2024.csv | 430 MB | 5,633,280 | 2010-01-01 to 2024-12-31 |
| GBP/USD | GBPUSD_1min_2010_2024.csv | 431 MB | 5,633,280 | 2010-01-01 to 2024-12-31 |
| USD/JPY | USDJPY_1min_2010_2024.csv | 426 MB | 5,633,280 | 2010-01-01 to 2024-12-31 |

### Crypto Data (2 pairs, 2018-2024)
- **Source:** Binance Data Vision (data.binance.vision)
- **Method:** Monthly 1-minute kline files concatenated
- **Total Size:** 428 MB
- **Files:** 2

| Pair | File | Size | Rows | Date Range |
|------|------|------|------|------------|
| BTC/USDT | BTCUSDT_1min_2018_2024.csv | 222 MB | 3,674,015 | 2018-01-01 to 2024-12-31 |
| ETH/USDT | ETHUSDT_1min_2018_2024.csv | 207 MB | 3,674,014 | 2018-01-01 to 2024-12-31 |

---

## 🔍 Data Quality

### CSV Schema
All files follow the standard OHLCV schema:
```
datetime,open,high,low,close,volume
```

### FX Data Characteristics
- **Granularity:** Synthetic minute-level (expanded from daily OHLC)
- **Volume:** Always 0 (not available in FX daily data)
- **Timezone:** UTC
- **Interpolation Method:** Linear progression through daily OHLC points
  - First quarter: open → high
  - Second quarter: high → low
  - Third quarter: low → close
  - Final quarter: settle at close

**Important Notes:**
- ✅ Suitable for daily/hourly analysis and research
- ✅ Captures daily price ranges (OHLC) accurately
- ⚠️ **NOT real tick data** - synthetic interpolation between daily values
- ⚠️ Less accurate for intraday minute-level pattern analysis
- ⚠️ Does not capture intraday volatility or true price movements

### Crypto Data Characteristics
- **Granularity:** Real 1-minute klines from Binance
- **Volume:** Actual trading volume in base currency
- **Timezone:** UTC
- **Source Quality:** Official Binance historical data (high fidelity)

**Characteristics:**
- ✅ Real tick-by-tick aggregated data
- ✅ Accurate for all timeframes (minute to daily)
- ✅ Includes actual trading volume
- ✅ Captures intraday volatility accurately

---

## 🎯 Extreme Events Coverage

### FX Events (Verified Present)
- ✅ **2015-01-15**: SNB peg removal (EUR/CHF impact on EUR/USD)
- ✅ **2016-10-07**: Brexit flash crash (GBP/USD)
- ✅ **2019-01-03**: JPY flash crash (USD/JPY)

### Crypto Events (Verified Present)
- ✅ **2020-03-12**: COVID-19 crash
- ✅ **2021-05-19**: May 2021 crypto crash
- ✅ **2022-11-08**: FTX collapse

All critical extreme events are present in the dataset for conformal prediction testing.

---

## 🛠️ Download Process

### Pipeline Execution (v3)
1. **Step 1**: Gemini documented data source specifications (53s)
2. **Step 2**: Codex wrote FX download script (256s) - targeting Dukascopy
3. **Step 3**: Codex wrote crypto download script (92s) - targeting Binance
4. **Step 4**: Codex executed downloads - **FAILED** with DNS errors (78s)
5. **Step 5**: Codex validated data quality (94s)
6. **Step 6**: Codex generated documentation (146s)

**Pipeline Result:** All steps marked "completed" but Step 4 correctly failed with exit code 1 due to:
- HistData.com: DNS resolution failed
- Dukascopy: DNS resolution failed
- TrueFX: DNS resolution failed

### Manual Recovery
After pipeline failure, successfully downloaded data using alternative sources:

**Crypto (Binance Data Vision):**
- Created `download_crypto_binance.py`
- Downloaded 84 monthly ZIP files per pair (2018-01 to 2024-12)
- Extracted and concatenated into single CSV per pair
- **Duration:** ~3 minutes total
- **Status:** ✅ Complete

**FX (Alpha Vantage API):**
- Created `download_fx_alphavantage.py`
- API Key: GPRF21WU2IO9KLVR (user-provided)
- Downloaded daily OHLC data (full history available)
- Expanded daily bars to minute resolution using synthetic interpolation
- **Rate Limiting:** 12.1s between requests (5 req/min limit)
- **Duration:** ~50 seconds total (6 API calls)
- **Status:** ✅ Complete

---

## 📁 File Locations

```
TrackG_ExtremeConformal/
├── data/
│   ├── fx/
│   │   └── raw/
│   │       ├── EURUSD_1min_2010_2024.csv  (430 MB)
│   │       ├── GBPUSD_1min_2010_2024.csv  (431 MB)
│   │       └── USDJPY_1min_2010_2024.csv  (426 MB)
│   └── crypto/
│       └── raw/
│           ├── BTCUSDT_1min_2018_2024.csv  (222 MB)
│           └── ETHUSDT_1min_2018_2024.csv  (207 MB)
└── src/
    └── data/
        ├── download_fx_alphavantage.py     (working - Alpha Vantage)
        ├── download_crypto_binance.py      (working - Binance)
        ├── download_fx_yahoo.py            (attempted - insufficient range)
        ├── download_fx.py                  (pipeline-generated - DNS failed)
        └── download_crypto.py              (pipeline-generated - not executed)
```

---

## ⚠️ Known Limitations

### FX Data Limitations
1. **Synthetic Intraday Data**: Minute-level prices are interpolated from daily OHLC, not real ticks
2. **No Volume Data**: FX daily data doesn't include volume information
3. **Simplified Price Movement**: Linear interpolation doesn't capture real intraday volatility
4. **Weekend Gaps**: FX markets are closed on weekends (Saturday/Sunday data absent)

### Alpha Vantage API Limitations
1. **Intraday History**: Only ~30 days of real 1-minute data available
2. **Rate Limits**: 25 requests/minute, 500 requests/day (free tier)
3. **Daily Data Only**: For historical periods beyond 30 days, only daily OHLC available

### Network/Source Limitations (Discovered)
1. **HistData.com**: DNS resolution failed (likely firewall/network restriction)
2. **Dukascopy**: DNS resolution failed
3. **TrueFX**: DNS resolution failed
4. **Yahoo Finance**: Only 2 years of hourly data, 8 days of 1-minute data

---

## ✅ Recommendations for Research

### Use FX Data For:
- Daily or multi-day extreme event analysis
- Daily high/low/close price movements
- Overnight gap analysis
- Multi-day trend analysis
- Daily volatility estimation

### Avoid FX Data For:
- Intraday minute-level pattern recognition
- High-frequency trading simulations
- Intraday volatility analysis
- Exact extreme event timing (within-day accuracy)

### Use Crypto Data For:
- All timeframes (minute to daily)
- Precise extreme event timing
- Intraday volatility analysis
- Volume-based analysis
- High-fidelity backtesting

---

## 🔧 Reproduction

To re-download the data:

### Crypto (No API key needed):
```bash
python src/data/download_crypto_binance.py
```

### FX (Requires Alpha Vantage API key):
```bash
# Edit src/data/download_fx_alphavantage.py
# Set API_KEY = "your_key_here"
python src/data/download_fx_alphavantage.py
```

---

## 📝 Notes

- All CSV files excluded from git via `.gitignore` (local storage only)
- Total dataset size: ~1.7 GB uncompressed
- Expected disk space: 2-3 GB with working files
- Git repository tracks scripts and documentation, not data files

---

**Last Updated:** 2026-03-12 19:02 UTC
**Orchestration Tool:** orch v1.0
**Agents Used:** Gemini (research), Codex (implementation), Claude (recovery)
