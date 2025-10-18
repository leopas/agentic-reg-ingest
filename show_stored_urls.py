#!/usr/bin/env python3
"""Show stored URLs from search_result table."""

import sys
sys.path.insert(0, ".")

from db.session import DatabaseSession
from sqlalchemy import text

db = DatabaseSession()
session = next(db.get_session())

# Stats
result = session.execute(
    text("SELECT COUNT(*) as total, SUM(approved) as approved FROM search_result")
).fetchone()

print("=" * 80)
print("📊 ESTATÍSTICAS: search_result")
print("=" * 80)
print(f"  Total URLs: {result[0]}")
print(f"  Aprovadas: {result[1]}")
print()

# Get a plan_id from vision_upload
plan_result = session.execute(
    text("SELECT plan_id FROM vision_upload WHERE plan_id IS NOT NULL LIMIT 1")
).fetchone()

if plan_result:
    plan_id = plan_result[0]
    
    # Get URLs from search_result
    urls = session.execute(
        text("""
            SELECT sr.url, sr.title, sr.score, sr.approved, sr.final_type
            FROM search_result sr
            ORDER BY sr.created_at DESC
            LIMIT 10
        """)
    ).fetchall()
    
    print("=" * 80)
    print(f"📋 URLS RECENTES (plan_id: {plan_id[:24]}...)")
    print("=" * 80)
    
    if urls:
        for idx, u in enumerate(urls, 1):
            url, title, score, approved, final_type = u
            status = "✅" if approved else "❌"
            print(f"\n{idx}. {status} {url[:70]}...")
            print(f"   Título: {title[:60] if title else 'N/A'}...")
            print(f"   Score: {score} | Tipo: {final_type}")
    else:
        print("  (Nenhuma URL encontrada)")
    
    print()
    print("=" * 80)
    print("📍 LOCALIZAÇÃO:")
    print("=" * 80)
    print("  Tabela: search_result")
    print("  Ligação: vision_upload.plan_id → agentic_plan.plan_id")
    print("           agentic_iter.approved_urls (JSON) lista as URLs")
    print("           search_result armazena detalhes completos")
    print("=" * 80)
else:
    print("⚠️  Nenhum plan_id encontrado em vision_upload")

