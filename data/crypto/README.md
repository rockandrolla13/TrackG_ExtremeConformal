# Crypto Data

## Source

The data is intended to be downloaded from [CryptoDataDownload.com](https://www.cryptodatadownload.com/data/).

## Download Method

The data can be downloaded using the `src/data/download_crypto.py` script.
The script attempts to download 1-minute data for the following pairs from Binance:
- BTC/USDT
- ETH/USDT

## Timezone

The data is assumed to be in **UTC**, which is standard for cryptocurrency exchanges. This should be verified after download.

## Issues

- The download script `src/data/download_crypto.py` uses a guessed URL format. If the download fails, the URLs in the script will need to be corrected. The website was ambiguous about whether 1-minute data requires a paid subscription. The script assumes it is freely available at a predictable URL.
- If the URLs are incorrect, the data may need to be downloaded manually from the website.
