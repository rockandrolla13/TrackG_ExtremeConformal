import requests
import os

# Configuration
BASE_URL_TEMPLATE = "https://www.cryptodatadownload.com/cdd/Binance_{pair}_{timeframe}.csv"
OUTPUT_DIR = "data/crypto/raw"
PAIRS = ["BTCUSDT", "ETHUSDT"]
TIMEFRAME = "1min" # Guessing the timeframe string in the URL


def download_crypto_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for pair in PAIRS:
        # Construct URL
        url = BASE_URL_TEMPLATE.format(pair=pair, timeframe=TIMEFRAME)

        # File naming
        filename = f"{pair}_{TIMEFRAME}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Check if file already exists
        if os.path.exists(filepath):
            print(f"Skipping {filename}, already exists.")
            continue

        print(f"Downloading {pair}...")

        try:
            # Make the GET request to download the data
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()  # Raise an exception for bad status codes

            # Save the csv file
            with open(filepath, "w") as f:
                f.write(response.text)

            print(f"Successfully downloaded {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {pair}: {e}")
            print(f"Please check the URL: {url}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    download_crypto_data()
