# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""View agentic search iterations (audit trail)."""

import argparse
import json
import sys
from dotenv import load_dotenv

load_dotenv()

from db.dao import AgenticIterDAO
from db.session import DatabaseSession


def main():
    """View iterations for a plan."""
    parser = argparse.ArgumentParser(description="View agentic search iterations")
    parser.add_argument("plan_id", help="Plan ID (UUID)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    try:
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            iterations = AgenticIterDAO.get_iters(session, args.plan_id)
        
        if not iterations:
            print(f"❌ No iterations found for plan: {args.plan_id}")
            return 1
        
        if args.json:
            # JSON output
            print(json.dumps({
                "plan_id": args.plan_id,
                "total_iterations": len(iterations),
                "iterations": iterations,
            }, indent=2, ensure_ascii=False))
        else:
            # Pretty console output
            print("\n" + "="*80)
            print(f"📊 AGENTIC SEARCH AUDIT TRAIL")
            print(f"Plan ID: {args.plan_id}")
            print("="*80 + "\n")
            
            for iter_data in iterations:
                iter_num = iter_data["iter_num"]
                print(f"┌─ ITERATION {iter_num} ─────────────────────────────────────────────────")
                print(f"│ Time: {iter_data['created_at']}")
                print(f"│")
                print(f"│ 📝 Executed Queries ({len(iter_data['executed_queries'])}):")
                for q in iter_data['executed_queries']:
                    print(f"│   • {q}")
                print(f"│")
                print(f"│ ✅ Approved ({len(iter_data['approved_urls'])}):")
                for url in iter_data['approved_urls'][:5]:
                    url_short = '/'.join(url.split('/')[-2:])
                    print(f"│   ✓ {url_short}")
                    print(f"│     {url}")
                if len(iter_data['approved_urls']) > 5:
                    print(f"│   ... and {len(iter_data['approved_urls']) - 5} more")
                print(f"│")
                print(f"│ ❌ Rejected ({len(iter_data['rejected'])}) - COM MOTIVOS:")
                for r in iter_data['rejected'][:8]:
                    url_short = '/'.join(r['url'].split('/')[-2:])
                    print(f"│   ✗ {url_short}")
                    print(f"│     URL: {r['url']}")
                    print(f"│     💬 Razão: {r['reason']}")
                    if r.get('violations') and len(r['violations']) > 0:
                        print(f"│     🚫 Violations: {', '.join(r['violations'])}")
                    else:
                        print(f"│     🚫 Violations: (nenhuma específica)")
                    print(f"│")
                if len(iter_data['rejected']) > 8:
                    print(f"│   ... and {len(iter_data['rejected']) - 8} more rejeitados")
                print(f"│")
                print(f"│ 🔄 New Queries Proposed ({len(iter_data['new_queries'])}):")
                for q in iter_data['new_queries']:
                    print(f"│   → {q}")
                if len(iter_data['new_queries']) == 0:
                    print(f"│   (nenhuma query nova proposta)")
                print(f"│")
                if iter_data.get('summary'):
                    print(f"│ 📌 Summary: {iter_data['summary']}")
                print(f"└{'─'*77}\n")
            
            print("="*80)
            print(f"Total iterations: {len(iterations)}")
            total_approved = sum(len(i['approved_urls']) for i in iterations)
            total_rejected = sum(len(i['rejected']) for i in iterations)
            print(f"Total approved: {total_approved}")
            print(f"Total rejected: {total_rejected}")
            print("="*80 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

