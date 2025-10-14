#!/bin/bash
# bootstrap.sh - Bootstrap project dependencies

set -e

echo "Bootstrapping agentic-reg-ingest..."

# Upgrade pip
python -m pip install --upgrade pip

# Install pip-tools (optional, for dependency locking)
read -p "Install pip-tools for dependency management? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip install pip-tools
    echo "pip-tools installed. You can now run: pip-compile requirements.in"
fi

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Start MySQL: docker compose up -d mysql"
echo "  3. Initialize DB: make db-init"
echo "  4. Run search: make search"
echo "  5. Run ingest: make ingest"

