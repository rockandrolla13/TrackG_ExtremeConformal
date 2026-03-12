import requests
import os
from zipfile import ZipFile

# Configuration
BASE_URL = "https://www.histdata.com/get.php"
OUTPUT_DIR = "data/fx/raw"
PAIRS = ["EURUSD", "GBPUSD", "USDJPY"]
YEARS = range(2010, 2025)

# HistData POST request form data fields
# These are guesses based on website inspection.
# The 'tk' field is the most likely to be a problem.
# It might be a session token that needs to be fetched from the main page first.
FORM_DATA = {
    "tk": "",  # This might need to be a dynamic token
    "date": "",  # YYYY
    "datemonth": "",  # YYYYMM
    "platform": "ASCII",
    "timeframe": "M1",
    "fxpair": "",
}


def download_fx_data():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for pair in PAIRS:
        for year in YEARS:
            for month in range(1, 13):
                # Construct form data
                datemonth = f"{year}{month:02d}"
                form_data = FORM_DATA.copy()
                form_data["date"] = str(year)
                form_data["datemonth"] = datemonth
                form_data["fxpair"] = pair

                # File naming
                zip_filename = f"HISTDATA_COM_ASCII_{pair}_M1{datemonth}.zip"
                zip_filepath = os.path.join(OUTPUT_DIR, zip_filename)
                csv_filename = f"DAT_ASCII_{pair}_M1_{year}{month:02d}.csv"
                csv_filepath = os.path.join(OUTPUT_DIR, csv_filename)

                # Check if file already exists
                if os.path.exists(csv_filepath):
                    print(f"Skipping {csv_filename}, already exists.")
                    continue

                print(f"Downloading {pair} for {year}-{month:02d}...")

                try:
                    # Make the POST request to download the data
                    response = requests.post(BASE_URL, data=form_data)
                    response.raise_for_status()  # Raise an exception for bad status codes

                    # Save the zip file
                    with open(zip_filepath, "wb") as f:
                        f.write(response.content)

                    # Unzip the file
                    with ZipFile(zip_filepath, "r") as zip_ref:
                        zip_ref.extractall(OUTPUT_DIR)

                    # Rename extracted file
                    extracted_csv_name = zip_ref.namelist()[0]
                    os.rename(os.path.join(OUTPUT_DIR, extracted_csv_name), csv_filepath)


                    # Clean up the zip file
                    os.remove(zip_filepath)

                    print(f"Successfully downloaded and extracted {csv_filename}")

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {pair} for {year}-{month:02d}: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")


if __name__ == "__main__":
    download_fx_data()
