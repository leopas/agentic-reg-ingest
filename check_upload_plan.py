#!/usr/bin/env python3
"""Check upload and plan in database."""

import sys
sys.path.insert(0, ".")

from db.session import DatabaseSession
from db.upload_dao import VisionUploadDAO
from sqlalchemy import text

def main():
    db = DatabaseSession()
    session = db.SessionLocal()
    
    upload_id = "bb5bd187-5a30-44c5-874f-094ffd2eab74"
    
    # Get upload
    upload = VisionUploadDAO.find_by_upload_id(session, upload_id)
    
    if not upload:
        print(f"❌ Upload não encontrado: {upload_id}")
        return
    
    print("=" * 80)
    print("📤 UPLOAD INFO:")
    print("=" * 80)
    print(f"ID: {upload.id}")
    print(f"Status: {upload.status}")
    print(f"Plan ID: {upload.plan_id}")
    print(f"Created: {upload.created_at}")
    print(f"Updated: {upload.updated_at}")
    
    # Get plan
    if upload.plan_id:
        result = session.execute(
            text("SELECT plan_id, goal, created_at FROM agentic_plan WHERE plan_id = :pid"),
            {"pid": upload.plan_id}
        ).fetchone()
        
        if result:
            print("\n" + "=" * 80)
            print("📋 PLAN INFO:")
            print("=" * 80)
            print(f"Plan ID: {result[0]}")
            print(f"Goal: {result[1]}")
            print(f"Created: {result[2]}")
            
            # Get approved URLs
            urls = session.execute(
                text("""
                    SELECT url, domain, decision 
                    FROM search_results 
                    WHERE plan_id = :pid AND decision = 'approved'
                    LIMIT 10
                """),
                {"pid": upload.plan_id}
            ).fetchall()
            
            print(f"\n📌 URLs Aprovadas ({len(urls)}):")
            for url_row in urls:
                print(f"  - {url_row[1]} → {url_row[0][:60]}...")
    
    session.close()

if __name__ == "__main__":
    main()

