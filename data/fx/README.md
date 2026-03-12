# FX Data

## Source

The data was downloaded from [HistData.com](https://www.histdata.com/download-free-forex-data/).

## Download Method

The data was downloaded using the `src/data/download_fx.py` script.
The script automates the process of sending POST requests to HistData.com for each month of data from 2010 to 2024 for the following pairs:
- EUR/USD
- GBP/USD
- USD/JPY

The data is 1-minute OHLCV data.

## Timezone

The data is in **Eastern Standard Time (EST)**, as specified by HistData.com. This corresponds to GMT-5.

## Issues

- The download script `src/data/download_fx.py` relies on simulating a form submission to HistData.com. The `tk` form field is currently sent empty, which might cause the download to fail. If the downloads fail, this token may need to be dynamically scraped from the website.
- The data is downloaded in monthly chunks and then saved as individual CSV files. For analysis, these will likely need to be concatenated.
