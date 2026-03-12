# Technical Specifications for Data Sources

This document provides detailed technical specifications for downloading historical financial data from Dukascopy and Binance.

## FX Data: Dukascopy Specifications

Dukascopy provides high-quality tick and aggregated historical data for a wide range of FX pairs. Accessing this data programmatically can be complex due to proprietary formats and access methods.

-   **Base URL**: `https://www.dukascopy.com/swiss/english/marketwatch/historical/`
-   **Data Access**: While the web interface allows manual downloads, programmatic access is typically achieved via specialized tools or APIs that handle the connection, data conversion, and download process. There isn't a simple URL template for direct downloads of CSV data.
-   **File Format**: The raw data is in a proprietary binary format. It must be converted to a more usable format like CSV. Tools that access Dukascopy data usually perform this conversion automatically.
-   **CSV Schema (for 1-minute aggregated data)**:
    -   `Timestamp`: POSIX timestamp in milliseconds (e.g., `1672531200000`)
    -   `Bid Price`: Bid price at the open of the minute.
    -   `Ask Price`: Ask price at the open of the minute.
    -   `Bid Volume`: Bid volume for the minute.
    -   `Ask Volume`: Ask volume for the minute.
-   **Download Procedure (Conceptual)**:
    1.  **Authentication**: A session might need to be established. This may require free registration.
    2.  **Request**: A request is sent specifying the instrument, date range, and timeframe (e.g., tick or 1-minute).
    3.  **Download**: The data is downloaded in a binary format.
    4.  **Conversion**: The binary data is processed and converted into a CSV file.
-   **Known Limitations**:
    -   **Rate Limits**: Dukascopy may impose rate limits or block IPs that make excessive requests.
    -   **Complexity**: Direct programmatic access requires reverse-engineering their communication protocol or using third-party libraries designed for this purpose. A common approach is to use a Java client provided by Dukascopy.
    -   **Time Zone**: Timestamps are in UTC.

## Crypto Data: Binance Data Vision Specifications

Binance offers a public data repository for historical kline (candlestick) data via their "Binance Data Vision" project, which is a public S3 bucket.

-   **URL Template for Monthly 1m Klines**:
    `https://data.binance.vision/data/spot/monthly/klines/{SYMBOL}/{INTERVAL}/{SYMBOL}-{INTERVAL}-{YYYY}-{MM}.zip`
    -   `{SYMBOL}`: The trading pair in uppercase (e.g., `BTCUSDT`).
    -   `{INTERVAL}`: The kline interval (e.g., `1m`).
    -   `{YYYY}`: The four-digit year (e.g., `2023`).
    -   `{MM}`: The two-digit month (e.g., `01`).

-   **Example URLs (2023)**:
    -   `https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-2023-01.zip`
    -   `https://data.binance.vision/data/spot/monthly/klines/ETHUSDT/1m/ETHUSDT-1m-2023-07.zip`

-   **File Format**:
    -   The data is provided as a `.zip` file for each month.
    -   Inside the zip archive is a single `.csv` file named `{SYMBOL}-{INTERVAL}-{YYYY}-{MM}.csv`.

-   **CSV Schema (1-minute klines)**:
    1.  `open_time`: Kline open time (Unix timestamp in milliseconds).
    2.  `open`: Open price.
    3.  `high`: High price.
    4.  `low`: Low price.
    5.  `close`: Close price.
    6.  `volume`: Volume.
    7.  `close_time`: Kline close time (Unix timestamp in milliseconds).
    8.  `quote_asset_volume`: Quote asset volume.
    9.  `number_of_trades`: Number of trades.
    10. `taker_buy_base_asset_volume`: Taker buy base asset volume.
    11. `taker_buy_quote_asset_volume`: Taker buy quote asset volume.
    12. `ignore`: Unused field.

-   **Download Procedure (Step-by-Step)**:
    1.  **Construct URL**: Iterate through the desired years and months to construct the download URLs based on the template.
    2.  **Download ZIP**: Use a standard HTTP client (like `wget` or `curl`) to download the zip file.
    3.  **Extract CSV**: Unzip the downloaded file to extract the CSV data.
    4.  **Concatenate**: If data for multiple months is needed, concatenate the individual CSV files into a single file. It is important to handle headers correctly (i.e., keep the header from the first file and skip it for subsequent files).

-   **Time Zone**: All timestamps are in UTC.

## Alternative: TrueFX

TrueFX offers free historical tick data for several major FX pairs.

-   **URL**: `https://www.truefx.com/truefx-historical-downloads/`
-   **Download Procedure**:
    -   Navigate to the downloads page.
    -   Data is available in monthly `.zip` files.
    -   The file naming convention is typically `{PAIR}-{YYYY}-{MM}.zip` (e.g., `EURUSD-2023-01.zip`).
    -   Download the files for the desired pair and date range.
    -   Each zip file contains a CSV file with tick data.
-   **CSV Schema (Tick Data)**:
    1.  `Instrument`: The currency pair.
    2.  `Timestamp`: Formatted as `YYYYMMDD HH:MM:SS.mmm`.
    3.  `Bid`: Bid price.
    4.  `Ask`: Ask price.
-   **Limitations**:
    -   Data is only available as tick data, which may require aggregation for certain use cases.
    -   The download process is manual via the web interface.
