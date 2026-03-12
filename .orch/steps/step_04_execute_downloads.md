# Step 4: Execute downloads
**Timestamp:** 2026-03-12T15:41:44.385451

---

Execution failed as required.

`python src/data/download_fx.py` exited non-zero before any downloads completed. The failure was a DNS/name-resolution error for `www.histdata.com`, so the fail-fast wrapper stopped immediately with exit code `1`. Because FX failed, the crypto step was not started.

Current state:
- [data/fx/raw](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/data/fx/raw) exists but contains `0` CSV files.
- [data/crypto/raw](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/data/crypto/raw) exists but contains `0` CSV files.
- Required summary written to [step_04_summary.md](/media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal/.orch/steps/step_04_summary.md).

The step should remain failed until outbound DNS/network access to the data source is available and the download commands can be rerun.
