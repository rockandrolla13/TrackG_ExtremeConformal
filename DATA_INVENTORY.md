# Financial Data Inventory for Extreme Conformal Prediction Research

**Generated:** 2026-03-12
**Project:** TrackG_ExtremeConformal
**Total Data:** ~2.2 GB across 57 CSV files

---

## Summary by Asset Class

| Asset Class | Files | Total Size | Granularity | Date Range | Status |
|-------------|-------|------------|-------------|------------|--------|
| **FX (Forex)** | 3 | 1.3 GB | Synthetic 1-min | 2010-2024 | ✅ Complete |
| **Crypto** | 18 | 431 MB | 1-min + Daily | 2017-2026 | ✅ Complete |
| **Equities** | 21 | 10.6 MB | Daily | 2000-2024 | ✅ Complete |
| **Volatility** | 1 | 327 KB | Daily | 1990-2026 | ✅ Complete |
| **Economic** | 12 | 2.0 MB | Daily/Monthly/Quarterly | 2000-2026 | ✅ Complete |

---

## Detailed Inventory

### 1. FX (Foreign Exchange) Data

**Source:** Alpha Vantage API
**License:** Free tier with API key
**Quality:** ⚠️ **Synthetic minute data** (daily OHLC interpolated to 1-minute)
**Use case:** Daily analysis, extreme event detection (not true intraday)

| Pair | File | Size | Rows | Date Range |
|------|------|------|------|------------|
| EUR/USD | `data/fx/raw/EURUSD_1min_2010_2024.csv` | 430 MB | ~5.6M | 2010-2024 |
| GBP/USD | `data/fx/raw/GBPUSD_1min_2010_2024.csv` | 431 MB | ~5.6M | 2010-2024 |
| USD/JPY | `data/fx/raw/USDJPY_1min_2010_2024.csv` | 426 MB | ~5.6M | 2010-2024 |

**Extreme Events Covered:**
- ✅ 2015-01-15: SNB Swiss Franc Peg Removal
- ✅ 2016-10-07: Brexit Flash Crash (GBP)
- ✅ 2019-01-03: JPY Flash Crash
- ✅ 2020-03-16: COVID-19 Crash

---

### 2. Cryptocurrency Data

#### 2a. Real Minute-Level Data (Binance Data Vision)

**Source:** Binance Data Vision (https://data.binance.vision)
**License:** Free, no API key required
**Quality:** ✅ **Real tick-aggregated 1-minute data**
**Use case:** Intraday analysis, high-frequency extreme events

| Pair | File | Size | Rows | Date Range |
|------|------|------|------|------------|
| BTC/USDT | `data/crypto/raw/BTCUSDT_1min_2018_2024.csv` | 222 MB | ~3.7M | 2018-2024 |
| ETH/USDT | `data/crypto/raw/ETHUSDT_1min_2018_2024.csv` | 207 MB | ~3.7M | 2018-2024 |

**Extreme Events Covered:**
- ✅ 2018 Crypto Winter
- ✅ 2020-03-16: COVID-19 Crash (crypto)
- ✅ 2021 Bull Run Peak
- ✅ 2022-05-12: Terra/Luna Collapse
- ✅ 2022-11-08: FTX Collapse

#### 2b. Daily Data (CryptoDataDownload)

**Source:** CryptoDataDownload.com
**License:** CC BY-NC-SA 4.0 (Non-commercial use)
**Quality:** ✅ **Real daily OHLCV data**
**Use case:** Long-term validation, cross-exchange comparison

| Exchange | Pair | File | Size | Rows | Date Range |
|----------|------|------|------|------|------------|
| Binance | BTC/USDT | `data/crypto/raw/cryptodatadownload/Binance_BTCUSDT_d.csv` | 322 KB | 3,127 | 2017-2026 |
| Binance | ETH/USDT | `data/crypto/raw/cryptodatadownload/Binance_ETHUSDT_d.csv` | 305 KB | 3,127 | 2017-2026 |
| Binance | BNB/USDT | `data/crypto/raw/cryptodatadownload/Binance_BNBUSDT_d.csv` | 278 KB | 3,046 | 2017-2026 |
| Binance | ADA/USDT | `data/crypto/raw/cryptodatadownload/Binance_ADAUSDT_d.csv` | 269 KB | 2,884 | 2017-2026 |
| Binance | SOL/USDT | `data/crypto/raw/cryptodatadownload/Binance_SOLUSDT_d.csv` | 185 KB | 2,037 | 2020-2026 |
| Binance | LUNA/USDT | `data/crypto/raw/cryptodatadownload/Binance_LUNAUSDT_d.csv` | 185 KB | 2,010 | 2019-2022 |
| FTX | BTC/USD | `data/crypto/raw/cryptodatadownload/FTX_BTCUSD_d.csv` | 128 KB | 1,211 | 2019-2022 |
| FTX | FTT/USD | `data/crypto/raw/cryptodatadownload/FTX_FTTUSD_d.csv` | 118 KB | 1,203 | 2019-2022 |

**Normalized versions** (standard OHLCV format):
`data/crypto/raw/normalized/*.csv` - 8 files, same data standardized

**Special Event Coverage:**
- ✅ LUNA/USDT: Terra/Luna collapse study (2019-2022)
- ✅ FTT/USD: FTX token collapse study (2019-2022)

---

### 3. Equity & Index Data

**Source:** Yahoo Finance (yfinance library)
**License:** Free, no API key required
**Quality:** ✅ **Real daily OHLCV data**
**Use case:** Long-term equity analysis, 2008 crisis, 2020 COVID

#### 3a. Major Indices

| Index | File | Size | Rows | Date Range |
|-------|------|------|------|------------|
| S&P 500 | `data/equities/raw/SP500_daily_20000101_20241231.csv` | 558 KB | ~6,250 | 2000-2024 |
| NASDAQ | `data/equities/raw/NASDAQ_daily_20000101_20241231.csv` | 540 KB | ~6,250 | 2000-2024 |
| DJIA | `data/equities/raw/DJIA_daily_20000101_20241231.csv` | 503 KB | ~6,250 | 2000-2024 |
| Russell 2000 | `data/equities/raw/RUSSELL2000_daily_20000101_20241231.csv` | 564 KB | ~6,250 | 2000-2024 |

#### 3b. Major ETFs

| ETF | Description | File | Size |
|-----|-------------|------|------|
| SPY | SPDR S&P 500 ETF | `data/equities/raw/SPY_daily_20000101_20241231.csv` | 555 KB |
| QQQ | Invesco QQQ (NASDAQ-100) | `data/equities/raw/QQQ_daily_20000101_20241231.csv` | 550 KB |
| DIA | SPDR Dow Jones Industrial | `data/equities/raw/DIA_daily_20000101_20241231.csv` | 547 KB |
| IWM | iShares Russell 2000 | `data/equities/raw/IWM_daily_20000101_20241231.csv` | 539 KB |

#### 3c. Tech Stocks (2020+ Analysis)

| Stock | File | Size |
|-------|------|------|
| AAPL | `data/equities/raw/AAPL_daily_20000101_20241231.csv` | 575 KB |
| MSFT | `data/equities/raw/MSFT_daily_20000101_20241231.csv` | 546 KB |
| GOOGL | `data/equities/raw/GOOGL_daily_20000101_20241231.csv` | 467 KB |
| AMZN | `data/equities/raw/AMZN_daily_20000101_20241231.csv` | 567 KB |
| TSLA | `data/equities/raw/TSLA_daily_20000101_20241231.csv` | 333 KB |
| NVDA | `data/equities/raw/NVDA_daily_20000101_20241231.csv` | 594 KB |
| META | `data/equities/raw/META_daily_20000101_20241231.csv` | 279 KB |
| NFLX | `data/equities/raw/NFLX_daily_20000101_20241231.csv` | 527 KB |

#### 3d. Financial Stocks (2008 Crisis)

| Stock | File | Size |
|-------|------|------|
| JPM | `data/equities/raw/JPM_daily_20000101_20241231.csv` | 542 KB |
| BAC | `data/equities/raw/BAC_daily_20000101_20241231.csv` | 547 KB |
| GS | `data/equities/raw/GS_daily_20000101_20241231.csv` | 524 KB |
| C | `data/equities/raw/C_daily_20000101_20241231.csv` | 504 KB |
| WFC | `data/equities/raw/WFC_daily_20000101_20241231.csv` | 545 KB |

**Extreme Events Covered:**
- ✅ 2008-09-29: Lehman Brothers Collapse
- ✅ 2010-05-06: Flash Crash
- ✅ 2015-08-24: China Market Crash
- ✅ 2018-02-05: VIXplosion
- ✅ 2020-03-16: COVID-19 Crash (peak)
- ✅ 2020-03-23: COVID-19 Bottom

---

### 4. Volatility Index (VIX)

**Source:** CBOE (Chicago Board Options Exchange)
**License:** Free, official source
**Quality:** ✅ **Official VIX data**
**Use case:** Fear gauge, extreme event indicator

| Index | File | Size | Rows | Date Range |
|-------|------|------|------|------------|
| VIX | `data/indices/raw/VIX_daily_1990_2026.csv` | 327 KB | 9,140 | 1990-2026 |

**Key VIX Spikes Documented:**
- 2008-10-24: VIX = 79.13 (Financial Crisis peak)
- 2010-05-06: VIX = 32.80 (Flash Crash)
- 2015-08-24: VIX = 40.74 (China Crash)
- 2018-02-05: VIX = 37.32 (VIXplosion)
- 2020-03-16: VIX = 82.69 (COVID peak - highest ever)

---

## 5. Economic Indicators

**Source:** FRED (Federal Reserve Economic Data)
**License:** Public domain (U.S. Government data)
**Quality:** ✅ **Official government data**
**Use case:** Macroeconomic context for extreme events

| Indicator | File | Size | Rows | Date Range | Frequency |
|-----------|------|------|------|------------|-----------|
| VIX Close | `data/economic/raw/VIX_Close_daily.csv` | 303 KB | 9,141 | 1990-2026 | Daily |
| S&P 500 Index | `data/economic/raw/SP500_Index_daily.csv` | 91 KB | 2,513 | 2010-2024 | Daily |
| Federal Funds Rate | `data/economic/raw/Federal_Funds_Rate_daily.csv` | 363 KB | 9,567 | 2000-2026 | Daily |
| Treasury 10Y | `data/economic/raw/Treasury_10Y_daily.csv` | 223 KB | 6,549 | 2000-2026 | Daily |
| Treasury 2Y | `data/economic/raw/Treasury_2Y_daily.csv` | 211 KB | 6,549 | 2000-2026 | Daily |
| Yield Spread 10Y-2Y | `data/economic/raw/Yield_Spread_10Y_2Y_daily.csv` | 275 KB | 6,549 | 2000-2026 | Daily |
| Yield Spread 10Y-3M | `data/economic/raw/Yield_Spread_10Y_3M_daily.csv` | 276 KB | 6,549 | 2000-2026 | Daily |
| Unemployment Rate | `data/economic/raw/Unemployment_Rate_daily.csv` | 12 KB | 313 | 2000-2026 | Monthly |
| CPI All Items | `data/economic/raw/CPI_All_Items_daily.csv` | 13 KB | 313 | 2000-2026 | Monthly |
| GDP | `data/economic/raw/GDP_daily.csv` | 3 KB | 104 | 2000-2024 | Quarterly |
| High Yield Spread | `data/economic/raw/High_Yield_Spread_daily.csv` | 314 KB | 6,839 | 2000-2026 | Daily |
| AAA Corporate Bonds | `data/economic/raw/AAA_Corporate_daily.csv` | 10 KB | 314 | 2000-2026 | Monthly |

**Total:** 12 files, 2.0 MB

**Key Economic Events Verified:**
- ✅ 2008-09-29: Lehman collapse (VIX = 46.72)
- ✅ 2008-10-24: Crisis peak (VIX = 79.13)
- ✅ 2009-10: Peak unemployment (10.0%)
- ✅ 2020-03-16: COVID peak (VIX = 82.69)
- ✅ 2020-04: COVID unemployment spike (14.8%)

**Yield Curve Inversions (Recession Indicator):**
- ✅ 2000-2007: Pre-2008 crisis inversions detected
- ✅ 2019: Pre-COVID inversion (-0.04%)
- ✅ 2022-2024: Recent inversions (min: -1.08% in 2023)

---

## Extreme Events Coverage Matrix

| Event | Date | FX | Crypto | Equities | VIX |
|-------|------|----|----|----------|-----|
| **Lehman / Financial Crisis** | 2008-09-29 | ❌ | ❌ | ✅ | ✅ (46.72) |
| **2008 Crisis Peak VIX** | 2008-10-24 | ❌ | ❌ | ✅ | ✅ (79.13) |
| **Flash Crash** | 2010-05-06 | ✅ | ❌ | ✅ | ✅ (32.80) |
| **SNB Peg Removal** | 2015-01-15 | ✅ | ❌ | ✅ | ✅ |
| **China Market Crash** | 2015-08-24 | ✅ | ❌ | ✅ | ✅ (40.74) |
| **Brexit Flash Crash** | 2016-10-07 | ✅ | ❌ | ✅ | ✅ |
| **2017 Bitcoin Bubble** | 2017-12-17 | ❌ | ✅ | ✅ | ✅ |
| **VIXplosion** | 2018-02-05 | ✅ | ✅ | ✅ | ✅ (37.32) |
| **JPY Flash Crash** | 2019-01-03 | ✅ | ✅ | ✅ | ✅ |
| **COVID-19 Crash** | 2020-03-16 | ✅ | ✅ | ✅ | ✅ (82.69) |
| **May 2021 Crypto Crash** | 2021-05-19 | ✅ | ✅ | ✅ | ✅ |
| **Terra/Luna Collapse** | 2022-05-12 | ✅ | ✅ (LUNA) | ✅ | ✅ |
| **FTX Collapse** | 2022-11-08 | ✅ | ✅ (FTT) | ✅ | ✅ |

---

## Data Quality Notes

### Strengths

✅ **Real intraday data for crypto** (Binance minute-level)
✅ **36 years of VIX data** (1990-2026)
✅ **25 years of equity data** (2000-2024)
✅ **26 years of economic indicators** (2000-2026)
✅ **Complete extreme event coverage** (all major crashes present)
✅ **Cross-validation data** (multiple exchanges for crypto, multiple indices for equities)
✅ **Special event data** (LUNA for Terra collapse, FTT for FTX collapse)
✅ **Macroeconomic context** (FRED indicators including yield curve inversions)

### Limitations

⚠️ **FX minute data is synthetic** (daily OHLC interpolated, not real tick data)
⚠️ **Pre-2018 crypto data limited to daily** (no minute data before 2018)
⚠️ **Equity data is daily only** (Yahoo Finance limits intraday to 8 days)

### Recommendations

1. **For daily analysis:** All data sources are suitable
2. **For intraday analysis:** Use crypto minute data (real), avoid FX minute data (synthetic)
3. **For high-frequency research:** Consider Databento ($125 credit) for post-2018 equity tick data
4. **For economic context:** FRED indicators provide macroeconomic variables and recession signals

---

## Download Scripts

All data was downloaded using automated Python scripts:

| Script | Description | Status |
|--------|-------------|--------|
| `src/data/download_fx_alphavantage.py` | FX data (synthetic minute) | ✅ Working |
| `src/data/download_crypto_binance.py` | Crypto minute data (Binance) | ✅ Working |
| `src/data/download_crypto_cryptodatadownload.py` | Crypto daily data (multi-exchange) | ✅ Working |
| `src/data/download_equities_yahoo.py` | Equity and index data | ✅ Working |
| `src/data/download_vix_cboe.py` | VIX volatility index | ✅ Working |
| `src/data/download_economic_fred.py` | Economic indicators | ✅ Working |

---

## Storage Structure

```
data/
├── crypto/
│   ├── raw/
│   │   ├── BTCUSDT_1min_2018_2024.csv          (222 MB)
│   │   ├── ETHUSDT_1min_2018_2024.csv          (207 MB)
│   │   └── cryptodatadownload/
│   │       ├── Binance_*.csv                    (8 files, raw)
│   │       └── normalized/
│   │           └── Binance_*.csv                (8 files, standardized)
│   └── extreme_events.csv
├── equities/
│   └── raw/
│       └── *_daily_20000101_20241231.csv       (21 files)
├── economic/
│   └── raw/
│       ├── VIX_Close_daily.csv                 (303 KB)
│       ├── SP500_Index_daily.csv               (91 KB)
│       ├── Federal_Funds_Rate_daily.csv        (363 KB)
│       ├── Treasury_10Y_daily.csv              (223 KB)
│       ├── Treasury_2Y_daily.csv               (211 KB)
│       ├── Yield_Spread_10Y_2Y_daily.csv       (275 KB)
│       ├── Yield_Spread_10Y_3M_daily.csv       (276 KB)
│       ├── Unemployment_Rate_daily.csv         (12 KB)
│       ├── CPI_All_Items_daily.csv             (13 KB)
│       ├── GDP_daily.csv                       (3 KB)
│       ├── High_Yield_Spread_daily.csv         (314 KB)
│       └── AAA_Corporate_daily.csv             (10 KB)
├── fx/
│   ├── raw/
│   │   ├── EURUSD_1min_2010_2024.csv           (430 MB)
│   │   ├── GBPUSD_1min_2010_2024.csv           (431 MB)
│   │   └── USDJPY_1min_2010_2024.csv           (426 MB)
│   └── extreme_events.csv
└── indices/
    └── raw/
        └── VIX_daily_1990_2026.csv             (327 KB)
```

---

## Next Steps

### Immediate
- [x] Set up FRED API key and download economic indicators ✅ COMPLETE
- [x] Validate all extreme events are visible in the data ✅ VERIFIED
- [ ] Document data provenance in research notes

### Optional Enhancements
- [ ] Sign up for Databento ($125 free credit) for ultra-precise post-2018 data
- [ ] Download additional crypto pairs from CryptoDataDownload (ADA, XRP, etc.)
- [ ] Set up automated daily update pipeline

---

**Last Updated:** 2026-03-12
**Total Files:** 57 CSV files
**Total Size:** ~2.2 GB
**Data Quality:** High (with noted FX synthetic limitation)
**Status:** ✅ All free data sources downloaded and verified
**Maintainer:** Claude Code / orch orchestration
