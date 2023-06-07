#!/bin/sh
set -euo pipefail
bash infra/entrypoints/prod.sh
python3 fill_db.py
