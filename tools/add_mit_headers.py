#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Script to add MIT license headers to source files."""

import sys
from pathlib import Path

AUTHOR = "Leopoldo Carvalho Correia de Lima"
YEAR = "2025"

SPDX = "SPDX-License-Identifier: MIT"
COPY = f"Copyright (c) {YEAR} {AUTHOR}"

EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".sql", ".html", ".css", ".yaml", ".yml", ".md"}
EXCLUDE_DIRS = {"venv", ".venv", "node_modules", ".git", ".mypy_cache", ".pytest_cache", "__pycache__", "qdrant_storage"}
EXCLUDE_FILES = {"LICENSE", "README.md"}  # README will be manually updated


def has_spdx(text: str) -> bool:
    """Check if file already has SPDX header."""
    return "SPDX-License-Identifier: MIT" in text


def make_header(ext: str) -> str:
    """Generate appropriate header for file extension."""
    if ext in {".html", ".md"}:
        return f"<!-- {SPDX} | (c) {YEAR} {AUTHOR} -->\n\n"
    elif ext == ".css":
        return f"/* {SPDX} | (c) {YEAR} {AUTHOR} */\n\n"
    elif ext == ".sh":
        # Preserve shebang if present
        return f"# {SPDX}\n# {COPY}\n\n"
    else:
        # Python, SQL, YAML, etc.
        return f"# {SPDX}\n# {COPY}\n\n"


def process_file(file_path: Path) -> bool:
    """Add header to file if missing. Returns True if modified."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"[skip] {file_path} - read error: {e}", file=sys.stderr)
        return False
    
    if has_spdx(text):
        return False
    
    ext = file_path.suffix.lower()
    header = make_header(ext)
    
    # Special handling for shell scripts with shebang
    if ext == ".sh" and text.startswith("#!"):
        lines = text.split("\n", 1)
        shebang = lines[0] + "\n"
        rest = lines[1] if len(lines) > 1 else ""
        new_text = shebang + header + rest
    else:
        new_text = header + text
    
    try:
        file_path.write_text(new_text, encoding="utf-8")
        print(f"[lic] ✅ {file_path}")
        return True
    except Exception as e:
        print(f"[skip] {file_path} - write error: {e}", file=sys.stderr)
        return False


def main():
    """Process all source files in repository."""
    root = Path(".")
    modified = 0
    skipped = 0
    
    for file_path in root.rglob("*"):
        # Skip directories
        if not file_path.is_file():
            continue
        
        # Skip excluded files
        if file_path.name in EXCLUDE_FILES:
            continue
        
        # Skip excluded directories
        if any(part in EXCLUDE_DIRS for part in file_path.parts):
            continue
        
        # Check extension
        ext = file_path.suffix.lower()
        if ext not in EXTS:
            continue
        
        # Process file
        if process_file(file_path):
            modified += 1
        else:
            skipped += 1
    
    print(f"\n✅ Done! Modified: {modified}, Skipped: {skipped}")


if __name__ == "__main__":
    main()

