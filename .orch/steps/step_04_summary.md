FX download started by invoking `python src/data/download_fx.py` after confirming `data/fx/raw/` and `data/crypto/raw/` exist. The run failed immediately with a DNS resolution error while requesting `https://www.histdata.com/download-free-forex-data/?/ascii/1-minute-bar-quotes`, so no FX files were created and no file sizes could be recorded.

Per fail-fast instructions, the crypto download was not executed. Current state: `data/fx/raw/` and `data/crypto/raw/` remain empty, and no validation of expected outputs was performed because downloads did not complete.
