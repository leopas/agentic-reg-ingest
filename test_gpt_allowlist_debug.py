#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Debug GPT Allowlist Planner."""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import structlog
from dotenv import load_dotenv

from agentic.enrichment.gpt_allowlist_planner import GPTAllowlistPlanner
from agentic.llm import LLMClient

# Setup logging
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

# Load environment
load_dotenv()

def main():
    """Test GPT Allowlist Planner."""
    print("=" * 80)
    print("🔍 TESTE: GPT Allowlist Planner")
    print("=" * 80)
    
    # Check env vars
    print("\n📋 Variáveis de Ambiente:")
    print(f"  USE_REAL_GPT_ALLOWLIST: {os.getenv('USE_REAL_GPT_ALLOWLIST', 'NOT SET')}")
    print(f"  OPENAI_API_KEY: {'✅ SET' if os.getenv('OPENAI_API_KEY') else '❌ NOT SET'}")
    print(f"  OPENAI_MODEL: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    
    # Initialize LLMClient
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ OPENAI_API_KEY não configurada!")
        return
    
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = LLMClient(api_key=api_key, model=model)
    
    print(f"\n✅ LLMClient inicializado: {llm.model}")
    print(f"  hasattr(_call_chat_completion): {hasattr(llm, '_call_chat_completion')}")
    
    # Initialize Planner
    planner = GPTAllowlistPlanner(llm)
    print(f"✅ GPTAllowlistPlanner inicializado")
    
    # Test with actual JSONL
    jsonl_path = "data/output/jsonl/bb5bd187-5a30-44c5-874f-094ffd2eab74.jsonl"
    
    if not Path(jsonl_path).exists():
        print(f"\n❌ JSONL não encontrado: {jsonl_path}")
        return
    
    print(f"\n📄 Testando com: {jsonl_path}")
    
    try:
        plan = planner.plan(jsonl_path)
        
        print("\n" + "=" * 80)
        print("📊 RESULTADO:")
        print("=" * 80)
        print(f"\nGoal: {plan.goal}")
        print(f"\nDomínios ({len(plan.allow_domains)}):")
        for domain in plan.allow_domains:
            print(f"  - {domain}")
        
        print(f"\nQueries ({len(plan.queries)}):")
        for q in plan.queries:
            print(f"  - {q.q}")
            print(f"    Why: {q.why}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import logging
    main()

