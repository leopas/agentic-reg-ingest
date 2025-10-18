#!/usr/bin/env python3
"""Check for duplicate URLs in search_result."""

import sys
sys.path.insert(0, ".")

from db.session import DatabaseSession
from sqlalchemy import text

db = DatabaseSession()
session = next(db.get_session())

# Check duplicates
result = session.execute(text("""
    SELECT url, COUNT(*) as count
    FROM search_result
    GROUP BY url
    HAVING count > 1
    ORDER BY count DESC
    LIMIT 20
""")).fetchall()

print("=" * 80)
print("🔍 URLs DUPLICADAS:")
print("=" * 80)

if result:
    print(f"\nTotal de URLs duplicadas: {len(result)}\n")
    for url, count in result:
        print(f"  {count}x → {url[:70]}...")
else:
    print("\n✓ Nenhuma URL duplicada encontrada!")

print()

# Total stats
stats = session.execute(text("""
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT url) as unique_urls,
        SUM(approved) as approved
    FROM search_result
""")).fetchone()

print("=" * 80)
print("📊 ESTATÍSTICAS GERAIS:")
print("=" * 80)
print(f"  Total de registros: {stats[0]}")
print(f"  URLs únicas: {stats[1]}")
print(f"  Duplicatas: {stats[0] - stats[1]} registros extras")
print(f"  Aprovadas: {stats[2]}")
print("=" * 80)

