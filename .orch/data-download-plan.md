# Data Download Orchestration Implementation Plan

> **For agentic workers:** This is an orch pipeline setup task. Execute manually or use orch CLI directly. No subagent-driven-development needed.

**Goal:** Create orch pipeline YAML to orchestrate FX and crypto data download via Gemini + Codex agents

**Architecture:** Single YAML file defining 6-step sequential pipeline with fail-fast error handling

**Tech Stack:** orch CLI, YAML, multi-agent orchestration (Gemini, Codex)

---

## File Structure

This plan creates the following files:

```
TrackG_ExtremeConformal/
├── .orch/
│   └── data-download.yml          # NEW: Pipeline definition
├── data/
│   ├── fx/raw/                    # NEW: Ensure directory exists
│   └── crypto/raw/                # NEW: Ensure directory exists
```

**Note:** The pipeline itself will create:
- `src/data/download_fx.py` (Step 2)
- `src/data/download_crypto.py` (Step 3)
- `src/data/validate_data.py` (Step 5)
- `data/{fx,crypto}/README.md` and `extreme_events.csv` (Step 6)

---

## Task 1: Initialize orch in Project

**Files:**
- Create: `.orch/` directory
- Create: `data/fx/raw/` directory
- Create: `data/crypto/raw/` directory

- [ ] **Step 1: Navigate to project directory**

```bash
cd /media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal
```

- [ ] **Step 2: Initialize orch**

```bash
orch init
```

Expected output:
```
✓ Created AGENTS.md
✓ Created CLAUDE.md
✓ Created GEMINI.md
✓ Initialized .orch/ in /media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal
```

- [ ] **Step 3: Create data directories**

```bash
mkdir -p data/fx/raw
mkdir -p data/crypto/raw
```

- [ ] **Step 4: Verify agent availability**

```bash
orch status
```

Expected: `gemini ✓` and `codex ✓` (at minimum)

- [ ] **Step 5: Commit initialization**

```bash
git add .orch/ AGENTS.md CLAUDE.md GEMINI.md data/
git commit -m "feat: initialize orch orchestration for data download"
```

---

## Task 2: Create Pipeline YAML

**Files:**
- Create: `.orch/data-download.yml`

- [ ] **Step 1: Create pipeline YAML file**

Create `.orch/data-download.yml` with the following content:

```yaml
name: "Historical Data Download for CL-G4 Extreme Conformal"
mode: sequential

steps:
  - name: "Research data sources"
    agent: gemini
    prompt_template: |
      You are researching free historical financial data sources for quantitative research.

      Read the requirements from: {project_dir}/data/DATA_DOWNLOAD_PROMPT.md

      SOURCES TO EVALUATE:
      1. HistData.com (https://www.histdata.com/download-free-forex-data/)
         - Check for: EUR/USD, GBP/USD, USD/JPY
         - Date range: 2010-2024
         - Format: CSV or ZIP with CSV

      2. Dukascopy (https://www.dukascopy.com/swiss/english/marketwatch/historical/)
         - Backup source for FX data
         - Check if free registration required

      3. CryptoDataDownload (https://www.cryptodatadownload.com/data/)
         - Check for: BTC/USD, ETH/USD
         - Date range: 2018-2024
         - Exchange: Binance or Coinbase

      FOR EACH SOURCE:
      - Verify pairs available (use web search if needed)
      - Check exact date ranges available
      - Document download method (direct URL, form submission, API)
      - Note file formats (CSV, ZIP, compression)
      - Identify any obstacles (auth, CAPTCHA, rate limits)

      KNOWN EXTREME EVENTS TO VERIFY:
      - FX: 2015-01-15 (SNB), 2016-10-07 (Brexit), 2019-01-03 (JPY flash)
      - Crypto: 2020-03-12 (COVID), 2021-05-19 (May crash), 2022-11-08 (FTX)

      Provide a structured report with:
      - Recommended source per asset class (FX vs crypto)
      - Exact download URLs or step-by-step procedures
      - File format specifications
      - Any gotchas or warnings
    timeout: 600
    on_failure: stop

  - name: "Write FX download script"
    agent: codex
    prompt_template: |
      Based on the research findings: {prev_step_summary}

      Create src/data/download_fx.py that downloads FX historical data.

      REQUIREMENTS:
      - Pairs: EUR/USD, GBP/USD, USD/JPY
      - Date range: 2010-01-01 to 2024-12-31
      - Frequency: 1-minute OHLCV
      - Output directory: data/fx/raw/
      - File naming: {PAIR}_1min_2010_2024.csv (e.g., EURUSD_1min_2010_2024.csv)
      - CSV schema: datetime,open,high,low,close,volume

      CODE CONSTRAINTS:
      - Python 3.x with type hints
      - Dependencies: requests, pandas, zipfile ONLY (no proprietary APIs)
      - No API keys or authentication required
      - Progress logging (print statements showing download progress)
      - Resume capability (check if file exists, skip or append)
      - Rate limiting: 2-3 second delay between requests
      - Error handling: retry on network errors (max 3 attempts)
      - Extract ZIP files automatically if source provides compressed data

      IMPLEMENTATION GUIDELINES:
      - Use the recommended source from research findings
      - Add docstrings explaining download procedure
      - Include main() function that can be called from command line
      - Log file sizes and estimated completion times

      The script should be production-ready and runnable with: python src/data/download_fx.py
    timeout: 300
    on_failure: stop

  - name: "Write crypto download script"
    agent: codex
    prompt_template: |
      Based on the research findings: {prev_step_summary}

      Create src/data/download_crypto.py that downloads crypto historical data.

      REQUIREMENTS:
      - Pairs: BTC/USD (or BTC/USDT), ETH/USD (or ETH/USDT)
      - Date range: 2018-01-01 to 2024-12-31
      - Frequency: 1-minute OHLCV
      - Output directory: data/crypto/raw/
      - File naming: {PAIR}_1min_2018_2024.csv (e.g., BTCUSD_1min_2018_2024.csv)
      - CSV schema: datetime,open,high,low,close,volume

      CODE CONSTRAINTS:
      - Follow the same patterns as src/data/download_fx.py for consistency
      - Python 3.x with type hints
      - Dependencies: requests, pandas, zipfile ONLY
      - No API keys or authentication required
      - Same error handling, logging, resume logic as FX script

      EXCHANGE SELECTION:
      - Use whichever exchange (Binance or Coinbase) has longest history
      - Document choice in code comments

      The script should match download_fx.py in style and functionality.
      Runnable with: python src/data/download_crypto.py
    timeout: 300
    on_failure: stop

  - name: "Execute downloads"
    agent: codex
    prompt_template: |
      Execute the download scripts and save data to the specified directories.

      TASKS:
      1. Verify directories exist: data/fx/raw/, data/crypto/raw/
      2. Run: python src/data/download_fx.py
      3. Run: python src/data/download_crypto.py
      4. Log progress, file sizes, and any errors

      FAIL-FAST BEHAVIOR:
      - If FX download fails, log error and STOP (do not proceed to crypto)
      - If crypto download fails, log error and STOP
      - Do NOT proceed to validation if downloads incomplete

      EXPECTED OUTPUT:
      - data/fx/raw/EURUSD_1min_2010_2024.csv (~500MB-2GB)
      - data/fx/raw/GBPUSD_1min_2010_2024.csv (~500MB-2GB)
      - data/fx/raw/USDJPY_1min_2010_2024.csv (~500MB-2GB)
      - data/crypto/raw/BTCUSD_1min_2018_2024.csv (~200MB-1GB)
      - data/crypto/raw/ETHUSD_1min_2018_2024.csv (~200MB-1GB)

      After each script completes, verify:
      - Files exist and are non-empty
      - File sizes are reasonable (>100MB per file)
      - Log final file sizes

      This step may take 30-60 minutes depending on network speed.
    timeout: 3600
    on_failure: stop

  - name: "Validate data quality"
    agent: codex
    prompt_template: |
      Create and run src/data/validate_data.py to check data quality.

      VALIDATION CHECKS:

      1. Date Completeness:
         - Load each CSV file
         - Check for gaps > 1 day (except weekends for FX: Sat/Sun acceptable)
         - Verify start date is 2010-01-01 for FX, 2018-01-01 for crypto
         - Verify end date is close to 2024-12-31

      2. Extreme Events Present:
         FX files should contain these dates:
         - 2015-01-15 (SNB peg removal)
         - 2016-10-07 (Brexit flash crash)
         - 2019-01-03 (JPY flash crash)

         Crypto files should contain these dates:
         - 2020-03-12 (COVID crash)
         - 2021-05-19 (May 2021 crash)
         - 2022-11-08 (FTX collapse)

      3. Data Quality:
         - No negative prices (open, high, low, close all >= 0)
         - Volume not zero throughout (at least some non-zero volume)
         - High >= Low for each row
         - Close between Low and High

      4. File Sizes:
         - Reasonable sizes (100-500MB per year per pair)
         - Log actual file sizes

      5. Timezone:
         - Attempt to infer timezone from data
         - Document in validation report

      OUTPUT:
      - Create validation script: src/data/validate_data.py
      - Print validation report showing PASS/FAIL for each check
      - Exit with code 0 if all checks pass, non-zero if any fail

      Run the validation script and report results.
    timeout: 600
    on_failure: stop

  - name: "Generate documentation"
    agent: codex
    prompt_template: |
      Create comprehensive documentation for the downloaded data.

      TASKS:

      1. Create data/fx/README.md:
         ```markdown
         # FX Historical Data

         **Source:** [HistData.com or Dukascopy - use actual source]
         **Download Date:** [today's date: YYYY-MM-DD]
         **Pairs:** EUR/USD, GBP/USD, USD/JPY
         **Date Range:** 2010-01-01 to 2024-12-31
         **Frequency:** 1-minute OHLCV
         **Timezone:** [UTC or actual timezone from validation]
         **File Format:** CSV (datetime,open,high,low,close,volume)

         ## Files
         - EURUSD_1min_2010_2024.csv - [file size]
         - GBPUSD_1min_2010_2024.csv - [file size]
         - USDJPY_1min_2010_2024.csv - [file size]

         ## Known Issues
         [Document any gaps, anomalies, or caveats from validation]

         ## Extreme Events Captured
         - 2015-01-15: SNB peg removal (Swiss franc)
         - 2016-10-07: Brexit flash crash (Sterling)
         - 2019-01-03: JPY flash crash
         ```

      2. Create data/crypto/README.md:
         Similar format for crypto, using actual exchange and source

      3. Create data/fx/extreme_events.csv:
         ```csv
         datetime,event,description
         2015-01-15 09:30:00,SNB_PEG_REMOVAL,Swiss National Bank removed EUR/CHF peg
         2016-10-07 07:00:00,BREXIT_FLASH_CRASH,Sterling flash crash on Brexit uncertainty
         2019-01-03 07:30:00,JPY_FLASH_CRASH,Japanese yen flash crash during Asian session
         ```

      4. Create data/crypto/extreme_events.csv:
         ```csv
         datetime,event,description
         2020-03-12 18:00:00,COVID_CRASH,COVID-19 pandemic market crash
         2021-05-19 12:00:00,MAY_2021_CRASH,Crypto market crash on China mining ban
         2022-11-08 08:00:00,FTX_COLLAPSE,FTX exchange collapse and market contagion
         ```

      5. Commit all documentation to git:
         ```bash
         git add data/fx/README.md data/crypto/README.md
         git add data/fx/extreme_events.csv data/crypto/extreme_events.csv
         git commit -m "docs: add data provenance and extreme events documentation"
         ```

      Ensure all documentation is production-ready and accurately reflects the actual download.
    timeout: 300
    on_failure: stop
```

- [ ] **Step 2: Verify YAML syntax**

```bash
# Check if file was created
ls -lh .orch/data-download.yml

# Validate YAML syntax (optional, requires yamllint)
# yamllint .orch/data-download.yml
```

- [ ] **Step 3: Dry-run the pipeline**

```bash
orch pipeline run .orch/data-download.yml --dry-run
```

Expected output: Shows 6 steps with agent assignments

- [ ] **Step 4: Commit pipeline definition**

```bash
git add .orch/data-download.yml
git commit -m "feat: add data download pipeline YAML definition"
```

---

## Task 3: Set Up Git Remote and Push

**Files:**
- Modify: `.git/config` (via git remote add)

- [ ] **Step 1: Check current remote status**

```bash
git remote -v
```

Expected: Empty (no remotes configured yet)

- [ ] **Step 2: Add remote repository**

**Note:** User needs to provide the remote repository URL

```bash
# Example (replace with actual URL):
git remote add origin https://github.com/username/TrackG_ExtremeConformal.git

# Or for SSH:
# git remote add origin git@github.com:username/TrackG_ExtremeConformal.git
```

- [ ] **Step 3: Push to remote**

```bash
git push -u origin main
```

Expected: All commits pushed, including design doc, plan, and pipeline YAML

- [ ] **Step 4: Verify remote tracking**

```bash
git branch -vv
```

Expected: `main` branch shows remote tracking

---

## Execution Instructions

### To run the pipeline:

```bash
# Navigate to project
cd /media/ak/10E1026C4FA6006E/GitRepos/TrackG_ExtremeConformal

# Execute pipeline in headless mode
orch pipeline run .orch/data-download.yml --headless

# Monitor progress (in separate terminal)
watch -n 10 'orch step status'

# Or check logs
orch step log
```

### Expected runtime:
- Total: ~45-90 minutes (mostly Step 4: downloads)
- Step 1: 5-10 min
- Step 2: 2-3 min
- Step 3: 2-3 min
- Step 4: 30-60 min (network dependent)
- Step 5: 5-10 min
- Step 6: 2-3 min

### If pipeline fails:

```bash
# Check status
orch step status

# Read error log
cat .orch/steps/step_XX_*.md

# Fix issue (update URL, script, etc.)

# Retry from failed step
orch step retry

# Or skip
orch step skip

# Resume rest of pipeline
orch resume --headless
```

---

## Success Criteria

Pipeline setup is complete when:

- [x] `.orch/` directory initialized
- [x] `data/fx/raw/` and `data/crypto/raw/` directories exist
- [x] `.orch/data-download.yml` created with 6 steps
- [x] YAML syntax validated (dry-run passes)
- [x] Git remote configured
- [x] All files committed and pushed

Pipeline execution is complete when:

- [ ] All 6 steps executed successfully
- [ ] 5 CSV files downloaded (3 FX, 2 crypto)
- [ ] All validation checks pass
- [ ] Documentation files created
- [ ] Everything committed to git

---

## Notes

**This is a setup/configuration task, not a code development task.** The actual implementation (download scripts, validation) will be done BY the pipeline agents (Codex) when the pipeline executes.

**No TDD cycle needed** because we're creating a YAML configuration file, not writing code that needs testing.

**The pipeline itself orchestrates the code generation** - Codex agents will write download_fx.py, download_crypto.py, and validate_data.py during pipeline execution.

---

## References

- Design spec: `docs/orch-data-download-design.md`
- Requirements: `data/DATA_DOWNLOAD_PROMPT.md`
- orch docs: `/home/ak/orch/README.md`
- Pipeline examples: `/home/ak/orch/examples/`
