# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""CLI runner for Agentic Search with debug mode."""

import argparse
import json
import sys
from pathlib import Path

import structlog
from dotenv import load_dotenv

# Load .env
load_dotenv()

from agentic.cse_client import CSEClient
from agentic.llm import LLMClient
from agentic.schemas import Plan
from agentic.scoring import ResultScorer
from common.env_readers import load_yaml_with_env
from db.session import DatabaseSession
from pipelines.agentic_controller import run_agentic_search


# Configure logging
def configure_logging(debug: bool = False):
    """Configure structured logging."""
    if debug:
        # Pretty console output for debugging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
        )
    else:
        # JSON output for production
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
        )


logger = structlog.get_logger()


def main():
    """CLI entry point for agentic search."""
    parser = argparse.ArgumentParser(
        description="Run Agentic Search (Plan→Act→Observe→Judge→Re-plan)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # Interactive: Create plan from prompt
  python scripts/run_agentic.py --prompt "Buscar RNs da ANS sobre cobertura obrigatória"

  # Load plan from JSON file
  python scripts/run_agentic.py --plan-file my_plan.json

  # Dry-run (simulate without persisting to DB)
  python scripts/run_agentic.py --prompt "..." --dry-run

  # Debug mode (colorful console output)
  python scripts/run_agentic.py --prompt "..." --debug

  # Generate plan only (don't run)
  python scripts/run_agentic.py --prompt "..." --plan-only
        """,
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--prompt", help="Natural language prompt to generate plan")
    input_group.add_argument("--plan-file", help="Path to plan JSON file")
    input_group.add_argument("--plan-id", help="Load plan from DB by ID")
    
    # Execution options
    parser.add_argument("--plan-only", action="store_true", help="Generate plan only, don't run loop")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without persisting to DB")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with colored output")
    parser.add_argument("--output", help="Save plan to JSON file (for editing)")
    
    # Config overrides
    parser.add_argument("--config-cse", default="configs/cse.yaml", help="CSE config path")
    parser.add_argument("--config-db", default="configs/db.yaml", help="DB config path")
    parser.add_argument("--config-agentic", default="configs/agentic.yaml", help="Agentic config path")
    
    args = parser.parse_args()
    
    # Configure logging
    configure_logging(debug=args.debug)
    
    try:
        # Load configs
        cse_config = load_yaml_with_env(args.config_cse)
        agentic_config = load_yaml_with_env(args.config_agentic)
        
        # Initialize LLM
        from common.settings import settings
        
        llm = LLMClient(
            api_key=settings.openai_api_key,
            model=agentic_config["agentic"]["llm"]["model"],
            temperature=agentic_config["agentic"]["llm"]["temperature"],
            max_tokens=agentic_config["agentic"]["llm"]["max_tokens"],
        )
        
        # Get or create plan
        if args.prompt:
            logger.info("🤖 Generating plan from prompt...")
            plan = llm.plan_from_prompt(args.prompt)
            
            print("\n" + "="*80)
            print("📋 GENERATED PLAN")
            print("="*80)
            print(json.dumps(plan.dict(), indent=2, ensure_ascii=False))
            print("="*80 + "\n")
            
            # Save to file if requested
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(json.dumps(plan.dict(), indent=2, ensure_ascii=False), encoding='utf-8')
                logger.info(f"💾 Plan saved to: {output_path}")
            
            # Stop if plan-only
            if args.plan_only:
                logger.info("✅ Plan generation complete. Use --plan-file to execute it.")
                return 0
        
        elif args.plan_file:
            logger.info(f"📂 Loading plan from: {args.plan_file}")
            plan_dict = json.loads(Path(args.plan_file).read_text(encoding='utf-8'))
            plan = Plan(**plan_dict)
        
        elif args.plan_id:
            logger.info(f"🔍 Loading plan from DB: {args.plan_id}")
            db_session = DatabaseSession()
            with next(db_session.get_session()) as session:
                from db.dao import AgenticPlanDAO
                plan_dict = AgenticPlanDAO.get_plan(session, args.plan_id)
                if not plan_dict:
                    logger.error("❌ Plan not found in database")
                    return 1
                plan = Plan(**plan_dict)
        
        # Dry-run mode
        if args.dry_run:
            logger.info("🏃 DRY-RUN MODE: Simulating without DB persistence")
            print("\n" + "="*80)
            print("🔮 DRY-RUN SIMULATION")
            print("="*80)
            print(f"Goal: {plan.goal}")
            print(f"Queries: {len(plan.queries)}")
            for i, q in enumerate(plan.queries, 1):
                print(f"  {i}. {q.q} (k={q.k})")
            print(f"\nStop conditions:")
            print(f"  Min approved: {plan.stop.min_approved}")
            print(f"  Max iterations: {plan.stop.max_iterations}")
            print(f"\nQuality gates:")
            print(f"  Types: {plan.quality_gates.must_types}")
            print(f"  Max age: {plan.quality_gates.max_age_years} years")
            print(f"  Min score: {plan.quality_gates.min_score}")
            print(f"  Min anchors: {plan.quality_gates.min_anchor_signals}")
            print("="*80)
            print("\n⚠️  Dry-run complete. Use without --dry-run to execute for real.")
            return 0
        
        # Execute agentic search
        logger.info("🚀 Starting agentic search loop...")
        
        # Initialize clients
        cse = CSEClient(
            api_key=cse_config["api_key"],
            cx=cse_config["cx"],
            timeout=int(cse_config["timeout_seconds"]),
        )
        
        scorer = ResultScorer(cse_config)
        
        # Run with DB session
        db_session = DatabaseSession()
        with next(db_session.get_session()) as session:
            result = run_agentic_search(plan, session, cse, llm, scorer)
            session.commit()
        
        # Print results
        print("\n" + "="*80)
        print("🎉 AGENTIC SEARCH COMPLETE")
        print("="*80)
        print(f"Plan ID: {result.plan_id}")
        print(f"Iterations: {result.iterations}")
        print(f"Approved total: {result.approved_total}")
        print(f"Stopped by: {result.stopped_by}")
        print(f"\n📋 Promoted URLs ({len(result.promoted_urls)}):")
        for i, url in enumerate(result.promoted_urls[:20], 1):
            print(f"  {i}. {url}")
        
        if len(result.promoted_urls) > 20:
            print(f"  ... and {len(result.promoted_urls) - 20} more")
        
        print("\n🔍 View audit trail:")
        print(f"  GET /agentic/iters/{result.plan_id}")
        print(f"  Or: python scripts/view_agentic_iters.py {result.plan_id}")
        print("="*80 + "\n")
        
        logger.info("✅ Agentic search complete", plan_id=result.plan_id)
        
        return 0
    
    except KeyboardInterrupt:
        logger.warning("⚠️  Interrupted by user")
        return 130
    
    except Exception as e:
        logger.error("❌ Agentic search failed", error=str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

