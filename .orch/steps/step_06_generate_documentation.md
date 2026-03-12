# Step 6: Generate documentation
**Timestamp:** 2026-03-12T14:36:18.907976

---

Updated the FX/crypto data documentation to match the downloader sources and schema expectations, and normalized the extreme-events files to the requested timestamped format. This refreshes `data/fx/README.md` and `data/crypto/README.md` with provenance, date ranges, and file expectations, while explicitly noting that no raw CSVs are present yet. It also replaces the old `event,timestamp` layout with the new `datetime,event,description` schema in `data/fx/extreme_events.csv` and `data/crypto/extreme_events.csv`, and records the work summary in `.orch/steps/step_06_summary.md`.

Tests not run (docs-only change).

Next steps (optional):
1. Re-run the FX and crypto download scripts to populate `data/fx/raw` and `data/crypto/raw`.
2. Run `python src/data/validate_data.py` to fill in real file sizes, coverage, and timezone validation details.
