#!/usr/bin/env python3
"""Show details of the last upload."""

import sys
sys.path.insert(0, ".")

from db.session import DatabaseSession
from sqlalchemy import text

def main():
    db = DatabaseSession()
    session = db.SessionLocal()
    
    # Get last upload
    upload = session.execute(
        text("SELECT id, upload_id, original_filename, status, plan_id, created_at FROM vision_upload ORDER BY created_at DESC LIMIT 1")
    ).fetchone()
    
    if not upload:
        print("❌ Nenhum upload encontrado no banco!")
        return
    
    print("=" * 80)
    print("📤 ÚLTIMO UPLOAD:")
    print("=" * 80)
    print(f"ID: {upload[0]}")
    print(f"Upload ID: {upload[1]}")
    print(f"Arquivo: {upload[2]}")
    print(f"Status: {upload[3]}")
    print(f"Plan ID: {upload[4]}")
    print(f"Criado: {upload[5]}")
    
    if upload[4]:
        # Get plan
        plan = session.execute(
            text("SELECT plan_id, goal FROM agentic_plan WHERE plan_id = :pid"),
            {"pid": upload[4]}
        ).fetchone()
        
        if plan:
            print("\n" + "=" * 80)
            print("📋 PLAN GERADO:")
            print("=" * 80)
            print(f"Goal: {plan[1]}")
            
            # Check if goal contains technical or regulatory domains
            goal_lower = plan[1].lower()
            if "ans" in goal_lower or "anvisa" in goal_lower or "bacen" in goal_lower or "regulat" in goal_lower:
                print("  ✅ Goal menciona regulamentação!")
            elif "arxiv" in goal_lower or "production" in goal_lower or "llm" in goal_lower:
                print("  ⚠️ Goal menciona termos técnicos (pode ter usado placeholder)")
            
            # Get approved URLs
            urls = session.execute(
                text("""
                    SELECT url, domain, decision 
                    FROM search_results 
                    WHERE plan_id = :pid AND decision = 'approved'
                    LIMIT 15
                """),
                {"pid": upload[4]}
            ).fetchall()
            
            print(f"\n📌 URLs Aprovadas ({len(urls)}):")
            for url_row in urls:
                print(f"  - {url_row[1]}")
                
            # Analyze domains
            domains = [u[1] for u in urls]
            has_gov = any(".gov.br" in d for d in domains)
            has_ans = any("ans.gov.br" in d for d in domains)
            has_tech = any(d in ["arxiv.org", "openai.com", "github.com", "huggingface.co"] for d in domains)
            
            print("\n📊 Análise:")
            print(f"  Domínios .gov.br: {'✅ SIM' if has_gov else '❌ NÃO'}")
            print(f"  Domínios ANS/Anvisa/Bacen: {'✅ SIM' if has_ans else '❌ NÃO'}")
            print(f"  Domínios técnicos (arxiv/openai): {'⚠️ SIM' if has_tech else '✅ NÃO'}")
            
            if has_tech and not has_gov:
                print("\n❌ PROBLEMA DETECTADO: URLs são de sites técnicos, não regulatórios!")
                print("   Isso indica que o PLACEHOLDER foi usado, não o GPT real.")
    
    session.close()

if __name__ == "__main__":
    main()

