# Data Download Agent Prompt

**Purpose:** Download free historical data for CL-G4 (Extreme Conformal Prediction for Intraday Tail Events) empirical experiments.

**Output directory:** `/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/data/`

---

## Task 1: FX Tick/1-Minute Data

### Sources (in priority order)

1. **HistData.com** (preferred)
   - URL: https://www.histdata.com/download-free-forex-data/
   - Format: CSV (ASCII)
   - Pairs needed: EUR/USD, GBP/USD, USD/JPY
   - Frequency: 1-minute OHLCV (tick if available)
   - Date range: 2010-01-01 to 2024-12-31
   - Known extreme events to verify are captured:
     - SNB peg removal: 2015-01-15
     - Brexit flash crash: 2016-10-07
     - JPY flash crash: 2019-01-03

2. **Dukascopy** (backup)
   - URL: https://www.dukascopy.com/swiss/english/marketwatch/historical/
   - Requires free registration
   - Same pairs/dates as above

### Output Structure
```
data/
├── fx/
│   ├── raw/
│   │   ├── EURUSD_1min_2010_2024.csv
│   │   ├── GBPUSD_1min_2010_2024.csv
│   │   └── USDJPY_1min_2010_2024.csv
│   ├── README.md  # Document source, download date, any issues
│   └── extreme_events.csv  # Timestamps of known flash crashes
```

### CSV Schema Expected
```
datetime,open,high,low,close,volume
2015-01-15 09:30:00,1.2010,1.2015,1.0350,1.0400,999999
```

---

## Task 2: Crypto 1-Minute Data

### Source

**CryptoDataDownload** (preferred)
- URL: https://www.cryptodatadownload.com/data/
- Format: CSV
- Pairs needed: BTC/USD (or BTC/USDT), ETH/USD (or ETH/USDT)
- Exchange: Binance or Coinbase (whichever has longest history)
- Frequency: 1-minute OHLCV
- Date range: 2018-01-01 to 2024-12-31
- Known extreme events to verify:
  - COVID crash: 2020-03-12
  - May 2021 crash: 2021-05-19
  - FTX collapse: 2022-11-08

### Output Structure
```
data/
├── crypto/
│   ├── raw/
│   │   ├── BTCUSD_1min_2018_2024.csv
│   │   └── ETHUSD_1min_2018_2024.csv
│   ├── README.md  # Document source, exchange, download date
│   └── extreme_events.csv  # Timestamps of known crashes
```

### CSV Schema Expected
```
datetime,open,high,low,close,volume
2020-03-12 10:00:00,7500.00,7520.00,5800.00,5850.00,50000.0
```

---

## Validation Checklist

After download, verify:

- [ ] All date ranges complete (no gaps > 1 day except weekends for FX)
- [ ] Known extreme events are present in data
- [ ] No obvious data errors (negative prices, volume = 0 throughout)
- [ ] File sizes reasonable (1-min data ~100MB-500MB per year per pair)
- [ ] Timezones documented in README (UTC preferred)

---

## Code Constraints

- Use Python with `requests`, `pandas`, `zipfile` only (no proprietary APIs)
- Handle rate limiting gracefully (sleep between requests)
- Save intermediate progress (can resume if interrupted)
- Do NOT require API keys (free public data only)
- Write download script to `src/data/download_fx.py` and `src/data/download_crypto.py`

---

## Success Criteria

Agent is done when:
1. All 5 CSV files exist in `data/{fx,crypto}/raw/`
2. README.md in each subdirectory documents provenance
3. `extreme_events.csv` lists timestamps of known crashes
4. Validation checklist passes
5. Download scripts are committed to `src/data/`
