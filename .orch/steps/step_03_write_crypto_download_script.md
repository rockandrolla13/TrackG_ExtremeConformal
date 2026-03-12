# Step 3: Write crypto download script
**Timestamp:** 2026-03-12T17:32:51.869371

---

Updated [src/data/download_crypto.py](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/src/data/download_crypto.py#L63) to align more closely with the FX downloader’s failure semantics and logging style. The Binance Data Vision monthly downloader remains the data source for `BTCUSDT` and `ETHUSDT`, writes `data/crypto/raw/{PAIR}_1min_2018_2024.csv`, preserves resume/skip behavior, and now guarantees `SystemExit(1)` on unrecoverable failure from [main()]( /media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/src/data/download_crypto.py#L211 ).

Expanded [tests/test_download_crypto.py](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/tests/test_download_crypto.py#L93) to cover non-ZIP download rejection, CLI exit-code behavior, and the top-level pair loop, and wrote the requested two-paragraph summary to [step_03_summary.md](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/.orch/steps/step_03_summary.md#L1).

Verification: `python -m py_compile src/data/download_crypto.py tests/test_download_crypto.py` passed. `pytest tests/test_download_crypto.py` could not run because `pandas` is not installed in this environment.
