#!/bin/bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

# run_search.sh - Execute search pipeline

set -e

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run search pipeline
python pipelines/search_pipeline.py \
    --config configs/cse.yaml \
    --db configs/db.yaml \
    --query "${1:-RN 259 ANS}" \
    --topn "${2:-100}"

