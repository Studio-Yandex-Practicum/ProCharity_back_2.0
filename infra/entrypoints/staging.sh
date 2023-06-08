#!/bin/sh
set -eu
bash infra/entrypoints/prod.sh
python3 fill_db.py
