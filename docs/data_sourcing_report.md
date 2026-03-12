# Historical Financial Data Sourcing Report

This report details the investigation into free historical data sources for FX and cryptocurrency data for quantitative research.

## 1. FX Data Source Evaluation

### Recommended Source: HistData.com

- **URL:** [https://www.histdata.com/download-free-forex-data/](https://www.histdata.com/download-free-forex-data/)
- **Available Pairs:** EUR/USD, GBP/USD, USD/JPY are all available.
- **Date Range:** Data is available from 2000 to present, covering the required 2010-2024 range.
- **Format:** 1-minute OHLCV data is available in ASCII (CSV) format, delivered in monthly `.zip` files.
- **Timezone:** EST (GMT-5).

### Download Procedure

A Python script, `src/data/download_fx.py`, has been created to automate the download process. The script works by sending POST requests that simulate the website's download form.

**Steps to use:**
1.  Run the script: `python src/data/download_fx.py`
2.  The script will download and unzip monthly data files into the `data/fx/raw/` directory.

### Gotchas and Warnings

- **Form Submission:** The script's success depends on the stability of HistData.com's form submission process. The `tk` field in the POST request is a potential point of failure and may need to be dynamically obtained if downloads fail.
- **Monthly Files:** The data is provided in monthly chunks. For analysis, these files will need to be concatenated into a single dataset per currency pair.
- **Rate Limiting:** Aggressive downloading may lead to IP blocking. The script does not currently implement any rate limiting, but it may be necessary to add `time.sleep()` calls if issues arise.

### Backup Source: Dukascopy

- **URL:** [https://www.dukascopy.com/swiss/english/marketwatch/historical/](https://www.dukascopy.com/swiss/english/marketwatch/historical/)
- **Evaluation:** Dukascopy provides high-quality data but requires a free registration and login. This makes it less suitable for fully automated, unattended scripting compared to HistData.com. It remains a strong backup option if manual intervention is acceptable.

## 2. Cryptocurrency Data Source Evaluation

### Recommended Source: CryptoDataDownload.com

- **URL:** [https://www.cryptodatadownload.com/data/](https://www.cryptodatadownload.com/data/)
- **Available Pairs:** BTC/USD(T) and ETH/USD(T) are available. Data from Binance and Coinbase is listed.
- **Date Range:** The required 2018-2024 period appears to be covered.
- **Format:** CSV files for 1-minute data are advertised.

### Download Procedure

A Python script, `src/data/download_crypto.py`, has been created to attempt downloads.

**Steps to use:**
1.  Run the script: `python src/data/download_crypto.py`
2.  The script will attempt to download files directly from URLs and save them to `data/crypto/raw/`.

### Gotchas and Warnings

- **URL Structure:** The download script uses a *guessed* URL structure (e.g., `.../Binance_BTCUSDT_1min.csv`). **This is a major assumption.** The website is not clear about the public availability of direct download links for 1-minute data, with some sections suggesting registration is required.
- **Verification Needed:** If the script fails, the URLs must be manually verified by visiting the website and inspecting the actual download links for the free data tiers. It's possible that no-registration downloads are only available for daily data, not 1-minute data.
- **Paid Tiers:** The site heavily promotes paid "Plus+" memberships. Care must be taken to only access the free data.

## 3. Coverage of Extreme Events

The recommended sources and date ranges should contain the data for the specified extreme market events. Verification should be performed after the data is successfully downloaded.

- **FX Events:** 2015-01-15 (SNB), 2016-10-07 (Brexit), 2019-01-03 (JPY flash crash)
- **Crypto Events:** 2020-03-12 (COVID), 2021-05-19 (May crash), 2022-11-08 (FTX)
