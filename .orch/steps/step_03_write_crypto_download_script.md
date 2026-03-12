# Step 3: Write crypto download script
**Timestamp:** 2026-03-12T15:40:18.207118

---

Updated [download_crypto.py](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/src/data/download_crypto.py) to match the FX downloader’s structure and behavior: Binance Data Vision monthly 1-minute ZIPs for `BTCUSDT` and `ETHUSDT`, resume from the last timestamp, completion skipping, retry/error handling, size/ETA logging, and non-zero exit on unrecoverable failure via raised exceptions. It writes `data/crypto/raw/{PAIR}_1min_2018_2024.csv` with the required `datetime,open,high,low,close,volume` schema.

Expanded [test_download_crypto.py](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/tests/test_download_crypto.py) to cover the same helper surface as FX, and wrote the required 2-paragraph handoff in [step_03_summary.md](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/.orch/steps/step_03_summary.md).

Verification: `python -m compileall src/data/download_crypto.py tests/test_download_crypto.py` passed. `pytest -q tests/test_download_crypto.py` could not run here because `pandas` is not installed in the environment.
