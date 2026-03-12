# Step 3: Write crypto download script
**Timestamp:** 2026-03-12T14:26:49.561280

---

Added a Binance-based crypto downloader that mirrors the FX script’s flow (monthly ZIPs, retries, resume, ETA) and normalizes to the required OHLCV schema, plus focused pytest coverage for the core helpers. This keeps behavior consistent with `src/data/download_fx.py` while targeting BTCUSDT/ETHUSDT and the 2018–2024 range in `data/crypto/raw`.

**Details**
- Downloader implementation in `src/data/download_crypto.py`, with a comment documenting Binance as the longest no-auth source and the same logging/resume logic as FX.
- Tests in `tests/test_download_crypto.py` cover month iteration, URL construction, CSV parsing, and ZIP extraction.

Tests not run here (environment lacks dependencies).

Next steps if you want:
1. Run `pytest -q`
2. Run `python src/data/download_crypto.py`
