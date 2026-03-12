# Step 5: Validate data quality
**Timestamp:** 2026-03-12T14:33:02.422646

---

Implemented a data validation script to audit FX/crypto CSV quality and added unit tests for the helper logic. The validator in `src/data/validate_data.py` checks date completeness (with weekend handling for FX), required extreme-event dates, price/volume sanity, file size per year, and a timezone inference heuristic, then prints a PASS/FAIL report and exits non‑zero on any failure.

Details
- Added `src/data/validate_data.py` to scan `data/fx/raw` and `data/crypto/raw`, compute gaps, extremes, data-quality flags, and size expectations, and emit a per-file report.
- Added `tests/test_validate_data.py` to cover gap detection, missing extremes, timezone inference, date bounds, and core quality metrics.

Run results
- `python src/data/validate_data.py` → FAIL: no CSV files found under `data/fx/raw` or `data/crypto/raw`.
- `pytest tests/test_validate_data.py` → FAIL: `pandas` not installed in the current test environment.

Next steps (pick any)
1. Re-run the data downloads so CSVs exist, then re-run `python src/data/validate_data.py`.
2. Install `pandas` in the test environment and re-run `pytest tests/test_validate_data.py`.
