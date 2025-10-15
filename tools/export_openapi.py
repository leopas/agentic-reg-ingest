#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Export OpenAPI schema from FastAPI app."""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Export OpenAPI schema."""
    from apps.api.main import app
    
    # Get OpenAPI schema
    schema = app.openapi()
    
    # Write to file
    output = Path("docs/api/openapi.json")
    output.write_text(json.dumps(schema, indent=2))
    
    print(f"✅ OpenAPI schema exported to: {output}")
    print(f"   Endpoints: {len(schema.get('paths', {}))}")
    print(f"   Version: {schema.get('info', {}).get('version')}")

if __name__ == "__main__":
    main()

