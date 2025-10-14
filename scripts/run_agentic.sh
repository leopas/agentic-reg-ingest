#!/bin/bash
# Agentic Search Runner - Linux/Mac Wrapper
# Usage: ./scripts/run_agentic.sh "seu prompt aqui"

set -e

if [ -z "$1" ]; then
    echo ""
    echo "========================================"
    echo "  Agentic Search - Quick Runner"
    echo "========================================"
    echo ""
    echo "Usage:"
    echo "  ./scripts/run_agentic.sh \"Buscar RNs da ANS sobre prazos de atendimento\""
    echo ""
    echo "Options:"
    echo "  ./scripts/run_agentic.sh --example       Run with example plan (PDFs/ZIPs)"
    echo "  ./scripts/run_agentic.sh --html          Run with HTML-only plan"
    echo "  ./scripts/run_agentic.sh --view PLAN_ID  View iterations"
    echo "  ./scripts/run_agentic.sh --help          Show full help"
    echo ""
    exit 1
fi

if [ "$1" = "--example" ]; then
    echo "Running with example plan (PDFs/ZIPs)..."
    .venv/bin/python scripts/run_agentic.py --plan-file examples/agentic_plan_example.json --debug
    exit 0
fi

if [ "$1" = "--html" ]; then
    echo "Running with HTML-only plan..."
    .venv/bin/python scripts/run_agentic.py --plan-file examples/agentic_plan_html_only.json --debug
    exit 0
fi

if [ "$1" = "--view" ]; then
    if [ -z "$2" ]; then
        echo "Error: PLAN_ID required"
        echo "Usage: ./scripts/run_agentic.sh --view PLAN_ID"
        exit 1
    fi
    .venv/bin/python scripts/view_agentic_iters.py "$2"
    exit 0
fi

if [ "$1" = "--help" ]; then
    .venv/bin/python scripts/run_agentic.py --help
    exit 0
fi

# Run with prompt
echo ""
echo "========================================"
echo "  Agentic Search Starting..."
echo "========================================"
echo ""
.venv/bin/python scripts/run_agentic.py --prompt "$1" --debug

