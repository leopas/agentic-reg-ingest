#!/bin/bash
# run_ingest.sh - Execute ingest pipeline

set -e

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run ingest pipeline
python pipelines/ingest_pipeline.py \
    --config configs/ingest.yaml \
    --db configs/db.yaml \
    --limit "${1:-100}"

