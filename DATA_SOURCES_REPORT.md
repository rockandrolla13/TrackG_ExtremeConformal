# Financial Data Sources for Extreme Conformal Prediction Research

**Report Date:** 2026-03-12
**Project:** TrackG_ExtremeConformal
**Purpose:** Comprehensive data acquisition for extreme event prediction

---

## 📊 **Current Dataset Summary**

### Downloaded Files (6 total, ~1.7 GB)

| Asset Class | File | Size | Rows | Date Range | Granularity | Source |
|-------------|------|------|------|------------|-------------|--------|
| **FX** | EURUSD_1min_2010_2024.csv | 430 MB | 5.6M | 2010-2024 | Synthetic 1-min | Alpha Vantage |
| **FX** | GBPUSD_1min_2010_2024.csv | 431 MB | 5.6M | 2010-2024 | Synthetic 1-min | Alpha Vantage |
| **FX** | USDJPY_1min_2010_2024.csv | 426 MB | 5.6M | 2010-2024 | Synthetic 1-min | Alpha Vantage |
| **Crypto** | BTCUSDT_1min_2018_2024.csv | 222 MB | 3.7M | 2018-2024 | Real 1-min | Binance |
| **Crypto** | ETHUSDT_1min_2018_2024.csv | 207 MB | 3.7M | 2018-2024 | Real 1-min | Binance |
| **Indices** | VIX_daily_1990_2026.csv | 327 KB | 9,140 | 1990-2026 | Daily | CBOE |

### Extreme Events Coverage

| Event | Date | Asset Class | VIX Value | Status |
|-------|------|-------------|-----------|--------|
| **Lehman / Financial Crisis** | 2008-09-29 | Equities | 46.72 | ✅ VIX |
| **Flash Crash** | 2010-05-06 | Equities | 32.80 | ✅ VIX + FX |
| **SNB Peg Removal** | 2015-01-15 | FX | - | ✅ FX |
| **China Market Crash** | 2015-08-24 | Equities | 40.74 | ✅ VIX |
| **Brexit Flash Crash** | 2016-10-07 | FX | - | ✅ FX |
| **VIXplosion / Volmageddon** | 2018-02-05 | Volatility | 37.32 | ✅ VIX + Crypto |
| **JPY Flash Crash** | 2019-01-03 | FX | - | ✅ FX |
| **COVID-19 Crash** | 2020-03-16 | All Markets | 82.69 | ✅ All |
| **May 2021 Crypto Crash** | 2021-05-19 | Crypto | - | ✅ Crypto |
| **Terra/Luna Collapse** | 2022-05-12 | Crypto | - | ✅ Crypto |
| **FTX Collapse** | 2022-11-08 | Crypto | - | ✅ Crypto |

---

## 🔍 **Recommended Additional Data Sources**

### **Tier 1: Immediate Priority (Free & High Quality)**

#### 1. **CryptoDataDownload** - ⭐⭐ **TOP CRYPTO SOURCE**

**Why:** Best free crypto source, comprehensive coverage since 2017

**Coverage:**
- 1000+ cryptocurrencies
- 20+ exchanges (Binance, Kraken, Coinbase, Bitfinex, FTX historical, etc.)
- Minute-level granularity
- 2017-present

**Extreme Events:**
- ✅ 2017 Bitcoin Bubble
- ✅ 2018 Crypto Winter
- ✅ 2020 March Crash
- ✅ 2021 Bull Run
- ✅ 2022 Terra/Luna + FTX

**Access:**
- **URL:** https://www.cryptodatadownload.com/data/
- **Method:** Direct CSV download (no API key)
- **Cost:** Free (CC BY-NC-SA 4.0 license)

**Recommended Pairs to Download:**
- BTC/USD (Coinbase, Kraken)
- ETH/USD (Coinbase, Kraken)
- Additional: BNB, XRP, ADA, SOL, LUNA (for Terra collapse)

**Action:**
```bash
# Manual download from website or create scraper
# Alternative exchanges for cross-validation
```

---

#### 2. **Yahoo Finance (yfinance)** - ⭐⭐ **TOP EQUITIES SOURCE**

**Why:** Decades of free daily stock data, covers all major crashes

**Coverage:**
- S&P 500, NASDAQ, DJIA indices
- Individual stocks (10,000+)
- Back to 1962 for some tickers
- Daily: unlimited, 1-minute: 7 days only

**Extreme Events:**
- ✅ 2008 Financial Crisis
- ✅ 2010 Flash Crash
- ✅ 2015-2016 events
- ✅ 2020 COVID Crash

**Access:**
- **Library:** `pip install yfinance`
- **Cost:** Free
- **API:** No key needed

**Recommended Downloads:**
```python
import yfinance as yf

# Indices
sp500 = yf.download("^GSPC", start="2000-01-01", end="2024-12-31")
nasdaq = yf.download("^IXIC", start="2000-01-01", end="2024-12-31")

# Major Tech Stocks (for 2020 events)
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META"]
for symbol in symbols:
    data = yf.download(symbol, start="2010-01-01", end="2024-12-31")
```

---

#### 3. **FRED (Federal Reserve)** - ⭐⭐ **ECONOMIC INDICATORS**

**Why:** Official government data, ultra-reliable

**Coverage:**
- VIX (already downloaded)
- S&P 500 Index
- Economic indicators (GDP, unemployment, interest rates)
- 840,000+ time series

**Access:**
- **URL:** https://fred.stlouisfed.org/
- **API:** Free key at https://fred.stlouisfed.org/docs/api/api_key.html
- **Library:** `pip install fredapi`

**Recommended Series:**
- `SP500`: S&P 500 Index
- `VIXCLS`: VIX Close (already have from CBOE)
- `DFF`: Federal Funds Rate
- `T10Y2Y`: 10-Year minus 2-Year Treasury Spread

---

### **Tier 2: High Value with Limitations**

#### 4. **Databento** - ⭐ **HIGH-FREQUENCY POST-2018**

**Why:** Ultra-precise tick data, $125 free credit

**Coverage:**
- Stocks, options, futures, crypto
- Nanosecond precision
- **2018-present only**

**Best For:**
- 2020 COVID crash (ultra-precise timing)
- 2022 crypto crashes
- Options volatility analysis
- High-frequency research

**Limitations:**
- Missing pre-2018 events (2008, 2010)
- $125 credit may be consumed quickly

**Access:**
- **URL:** https://databento.com/
- **Signup:** https://databento.com/signup ($125 credit)
- **API:** Python client `pip install databento`

**Action:** Use credit strategically for specific high-precision analysis

---

#### 5. **Finnhub** - ⭐ **REAL-TIME SUPPLEMENT**

**Why:** Good free tier, real-time capable

**Coverage:**
- US stocks, global markets
- Real-time and historical
- 60 API requests/minute (free)

**Access:**
- **URL:** https://finnhub.io/
- **API Key:** https://finnhub.io/register (free)
- **Library:** `pip install finnhub-python`

**Use Case:** Supplement Yahoo Finance with additional tickers

---

#### 6. **Tiingo** - ⭐ **30+ YEAR HISTORY**

**Why:** Long history, 100 requests/day free

**Coverage:**
- Back to 1962 for some stocks
- 30+ years typical
- 100 requests/day limit

**Access:**
- **URL:** https://www.tiingo.com/
- **API Key:** Free signup
- **Library:** Available in R, Python

---

### **Tier 3: Academic/Specialized**

#### 7. **WRDS (Wharton Research)** - 🎓 **ACADEMIC ONLY**

**Coverage:**
- TAQ: Microsecond tick data 2003-present
- CRSP: 1925-2023 stock prices
- Compustat, OptionMetrics, etc.

**Access:** University affiliation required

**If Available:** Best institutional-quality data source

---

#### 8. **Kaggle Datasets** - 📦 **CURATED COLLECTIONS**

**Useful Datasets:**
- S&P 500 Stock Data
- Cryptocurrency Financial Data
- VIX Historical

**Access:** Free Kaggle account

**Use Case:** Pre-processed datasets for specific research questions

---

## 📥 **Immediate Next Steps**

### Phase 1: Expand Crypto Coverage (This Week)

**Priority:** Download from CryptoDataDownload

1. **Additional Crypto Pairs:**
   - BTC/USD from Coinbase (cross-validate Binance)
   - BTC/USD from Kraken (cross-validate)
   - LUNA/USD (for Terra collapse study)
   - FTT/USD (for FTX collapse study)

2. **Method:**
   - Visit https://www.cryptodatadownload.com/data/
   - Select exchange (Coinbase, Kraken, etc.)
   - Download minute CSVs for 2017-2024

### Phase 2: Equity Indices (This Week)

**Priority:** Download major indices using yfinance

1. **S&P 500 (^GSPC):** Daily 2000-2024
2. **NASDAQ (^IXIC):** Daily 2000-2024
3. **DJIA (^DJI):** Daily 2000-2024
4. **Major Tech Stocks:** AAPL, MSFT, NVDA, TSLA, META

**Script:**
```bash
python src/data/download_sp500_yahoo.py
```

### Phase 3: Databento Credit Usage (Next Week)

**Strategy:** Use $125 credit for specific high-value queries

1. **COVID Crash (2020-03-16):**
   - Download 1-second SPY data for crash day
   - Download VIX options chain during spike

2. **2022 Crypto Crash:**
   - CME Bitcoin Futures tick data during FTX collapse

3. **Estimate Cost:**
   - Check Databento pricing calculator
   - Prioritize highest-impact dates

### Phase 4: Economic Indicators (Ongoing)

**FRED API Downloads:**
1. Federal Funds Rate (monetary policy context)
2. Unemployment Rate (economic stress indicator)
3. Treasury Yield Spread (recession predictor)

---

## 🛠️ **Data Pipeline Setup**

### Automated Update Scripts

Create cron jobs or scheduled tasks:

```bash
# Daily updates (run at 6 AM)
0 6 * * * cd /path/to/project && python src/data/update_daily.py

# Weekly crypto updates (Sunday 2 AM)
0 2 * * 0 cd /path/to/project && python src/data/update_crypto.py
```

### Data Validation Workflow

1. Download → 2. Validate → 3. Document → 4. Commit

```python
# Standard validation checks
def validate_ohlcv(df):
    assert df['high'].min() >= df['low'].max(), "High < Low violation"
    assert df['close'].between(df['low'], df['high']).all(), "Close out of range"
    assert df['datetime'].is_monotonic_increasing, "Timestamp ordering broken"
```

---

## 📋 **Data Quality Matrix**

| Source | Granularity | History | Quality | Completeness | Use For |
|--------|-------------|---------|---------|--------------|---------|
| **Alpha Vantage FX** | Synthetic 1-min | 15 years | ⭐⭐⭐ | Daily 100%, Intraday Synthetic | Daily FX analysis |
| **Binance** | Real 1-min | 7 years | ⭐⭐⭐⭐⭐ | 100% | All crypto analysis |
| **CBOE VIX** | Daily | 36 years | ⭐⭐⭐⭐⭐ | 100% | Volatility research |
| **Yahoo Finance** | Daily | 50+ years | ⭐⭐⭐⭐ | 95%+ | Equity long-term |
| **CryptoDataDownload** | Minute | 8 years | ⭐⭐⭐⭐⭐ | 100% | Crypto validation |
| **Databento** | Nanosecond | 5 years | ⭐⭐⭐⭐⭐ | 100% | HFT, precise timing |
| **FRED** | Daily | Varies | ⭐⭐⭐⭐⭐ | 100% | Economic context |

---

## 🎯 **Coverage Summary by Event Type**

### Flash Crashes & Volatility Spikes
- ✅ 2010 Flash Crash: VIX + FX
- ✅ 2015 China Crash: VIX
- ✅ 2018 VIXplosion: VIX + Crypto
- ✅ 2020 COVID: VIX + FX + Crypto
- **Gap:** Need equity tick data for 2010 (only if Databento or WRDS)

### Currency Events
- ✅ 2015 SNB: FX (synthetic)
- ✅ 2016 Brexit: FX (synthetic)
- ✅ 2019 JPY Flash: FX (synthetic)
- **Limitation:** Daily OHLC only, not true intraday

### Cryptocurrency Collapses
- ✅ 2017 Bubble: Need from CryptoDataDownload
- ✅ 2018 Winter: Binance + CDD
- ✅ 2020 COVID: Binance
- ✅ 2021 Peaks: Binance
- ✅ 2022 Terra: Binance (need LUNA specifically)
- ✅ 2022 FTX: Binance

### Equity Market Crashes
- ✅ 2008 Crisis: VIX + need Yahoo equities
- ✅ 2020 COVID: VIX + need Yahoo equities
- **Gap:** Individual stock data (download via Yahoo)

---

## 💡 **Research Recommendations**

### For Daily Analysis
- ✅ **Use:** FX (Alpha Vantage), VIX (CBOE), Equities (Yahoo Finance)
- ✅ **Sufficient for:** Daily conformal prediction intervals

### For Intraday Analysis
- ✅ **Use:** Crypto (Binance real data)
- ⚠️ **Caution:** FX is synthetic
- ✅ **Best:** Databento for post-2018 equity/options intraday

### For High-Frequency Research
- ❌ **Current data insufficient** (no sub-minute equity)
- ✅ **Solution:** Use Databento $125 credit for specific events
- ✅ **Alternative:** Focus on crypto (real tick aggregation)

### For Cross-Asset Analysis
- ✅ **Coverage good** across FX, crypto, volatility
- **Gap:** Need equity daily data (easy fix via Yahoo)

---

## 📌 **Action Items**

### Immediate (This Session)
- [x] VIX data downloaded ✅
- [ ] Download S&P 500 via yfinance
- [ ] Download LUNA/USD, FTT/USD from CryptoDataDownload
- [ ] Create Yahoo Finance download script

### This Week
- [ ] Download major crypto pairs from CryptoDataDownload
- [ ] Download major tech stocks (AAPL, TSLA, NVDA, etc.)
- [ ] Set up FRED API key and download economic indicators
- [ ] Validate all extreme events present in data

### Next Week
- [ ] Sign up for Databento and plan $125 credit usage
- [ ] Create automated update pipeline
- [ ] Document all data provenance
- [ ] Run comprehensive validation suite

---

**Last Updated:** 2026-03-12
**Next Review:** After Phase 1 completion
**Maintainer:** Claude Code / orch orchestration
