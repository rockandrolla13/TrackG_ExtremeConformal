# Step 2: Write FX download script
**Timestamp:** 2026-03-12T15:38:15.261429

---

Implemented the FX downloader in [src/data/download_fx.py](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/src/data/download_fx.py). It targets HistData monthly 1-minute ZIP archives for `EURUSD`, `GBPUSD`, and `USDJPY`, writes consolidated CSVs to `data/fx/raw/`, supports resume from the last written timestamp, skips already complete files, logs progress with sizes and ETA, enforces a 2.5s delay between requests, retries network/invalid-ZIP failures up to 3 times, and raises on unrecoverable failure so `python src/data/download_fx.py` exits non-zero.

I also updated helper coverage in [tests/test_download_fx.py](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/tests/test_download_fx.py) and wrote the required 2-paragraph handoff in [.orch/steps/step_02_summary.md](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/.orch/steps/step_02_summary.md). Verification was limited to `python -m compileall` because `pytest` could not run in this environment: `pandas` is not installed locally.
