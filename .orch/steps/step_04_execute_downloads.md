# Step 4: Execute downloads
**Timestamp:** 2026-03-12T14:27:22.823561

---

FX download failed immediately due to DNS resolution when trying to reach `www.histdata.com`, so I stopped per fail-fast and did not run crypto. The FX script emitted warnings about `numexpr`/`bottleneck` versions, but the hard failure was a `requests.exceptions.ConnectionError` (`NameResolutionError`). Both `data/fx/raw/` and `data/crypto/raw/` remain empty; no file sizes to report. Summary written to `.orch/steps/step_04_summary.md`.

Logs (key error):
- `python src/data/download_fx.py` → `requests.exceptions.ConnectionError: HTTPSConnectionPool(host='www.histdata.com', port=443): Max retries exceeded ... Failed to resolve 'www.histdata.com'`

Possible next steps:
1. Verify network/DNS access to `www.histdata.com` from this environment, then re-run `python src/data/download_fx.py`.
2. If DNS is blocked, provide an alternative FX data source or a mirror URL so the script can be updated.
