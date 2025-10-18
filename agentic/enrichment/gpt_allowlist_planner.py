# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""GPT-based allowlist and query planner for enrichment."""

import json
import os
from pathlib import Path
from typing import Dict, Any

import structlog

from agentic.llm import LLMClient
from apps.api.schemas.vision_enrichment import AllowlistPlan

logger = structlog.get_logger()


class GPTAllowlistPlanner:
    """Generate allowlist and queries from document JSONL."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize planner.
        
        Args:
            llm_client: LLM client for GPT calls
        """
        self.llm = llm_client
    
    def plan(self, jsonl_path: str) -> AllowlistPlan:
        """
        Generate allowlist plan from document JSONL.
        
        Args:
            jsonl_path: Path to JSONL file with document analysis
            
        Returns:
            AllowlistPlan with domains, queries, and gates
        """
        path = Path(jsonl_path)
        
        if not path.exists():
            logger.error("allowlist_plan_file_not_found", path=str(path))
            raise FileNotFoundError(f"JSONL file not found: {path}")
        
        logger.info("allowlist_plan_start", file=path.name)
        
        try:
            # Load JSONL document
            document_lines = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        document_lines.append(json.loads(line))
            
            if not document_lines:
                logger.warning("allowlist_plan_empty_jsonl", file=path.name)
                return self._default_plan()
            
            # Build context summary
            context = self._build_context_summary(document_lines)
            
            # Generate plan via LLM
            plan = self._generate_plan_via_llm(context)
            
            logger.info(
                "allowlist_plan_done",
                domains=len(plan.allow_domains),
                queries=len(plan.queries),
            )
            
            return plan
        
        except Exception as e:
            logger.error("allowlist_plan_failed", error=str(e))
            raise
    
    def _build_context_summary(self, document_lines: list) -> str:
        """
        Build context summary from document lines.
        
        Args:
            document_lines: List of parsed JSONL lines
            
        Returns:
            Summarized context string
        """
        # Extract text from all pages
        texts = []
        inferences = []
        
        for line in document_lines:
            if "text" in line:
                texts.append(line["text"])
            
            if "guided_inferences" in line:
                for inf in line["guided_inferences"]:
                    if "hypothesis" in inf:
                        inferences.append(inf["hypothesis"])
        
        # Combine into summary (limit to ~2000 chars)
        combined = "\n".join(texts)
        if len(combined) > 2000:
            combined = combined[:2000] + "..."
        
        inference_text = "\n".join(inferences) if inferences else ""
        
        summary = f"Texto do documento:\n{combined}\n\nInferências:\n{inference_text}"
        
        return summary
    
    def _generate_plan_via_llm(self, context: str) -> AllowlistPlan:
        """
        Generate allowlist plan via LLM.
        
        Args:
            context: Document context summary
            
        Returns:
            AllowlistPlan
        """
        prompt = f"""Você é um especialista em pesquisa de informações confiáveis e curadoria de fontes.

CONTEXTO DO DOCUMENTO ANALISADO:
{context}

INSTRUÇÕES:

1. ANÁLISE DO CONTEÚDO:
   - Identifique o tema/domínio principal do documento (ex: tecnologia, saúde, finanças, direito, ciência, etc.)
   - Identifique conceitos-chave, tecnologias, metodologias ou tópicos específicos
   - Determine o nível técnico (acadêmico, técnico, regulatório, comercial, geral)

2. IDENTIFICAÇÃO DE FONTES CONFIÁVEIS:
   - Para o DOMÍNIO identificado, liste ~10 domínios/sites MAIS CONFIÁVEIS e AUTORITATIVOS
   - Considere diferentes tipos de fontes conforme o tema:
     * Tecnologia: docs oficiais, GitHub, Stack Overflow, blogs técnicos de referência
     * Saúde: .gov, OMS, institutos médicos, journals científicos (PubMed, Nature)
     * Ciência: arxiv.org, universidades top, journals peer-reviewed
     * Regulatório: órgãos governamentais, planalto.gov.br, agências reguladoras
     * Negócios: Harvard Business Review, McKinsey, institutos setoriais
     * Geral: Wikipedia (para overview), enciclopédias especializadas
   
   - PRIORIZE: Autoridades reconhecidas no setor, não necessariamente .gov
   - EVITE: Blogs pessoais, sites de notícias genéricas, agregadores de conteúdo

3. CRIAÇÃO DE QUERIES:
   - Crie 3-5 queries de busca ESPECÍFICAS baseadas no conteúdo analisado
   - Queries devem buscar:
     * Aprofundamento de conceitos mencionados
     * Fontes primárias (papers, documentação oficial, estudos)
     * Casos de uso ou implementações práticas
     * Perspectivas complementares de autoridades no assunto
   
   - Use técnicas de busca avançada quando aplicável (site:, filetype:, etc.)

4. QUALITY GATES:
   - Ajuste conforme o domínio:
     * Documentação técnica: aceite .md, .html, .pdf
     * Acadêmico: priorize .pdf (papers)
     * Regulatório: priorize .pdf, .html
   - Idade máxima: 3 anos (padrão), mas considere se o tema evolui rápido (ex: AI = 1 ano)
   - Score mínimo: 0.7 (padrão)

FORMATO DE RESPOSTA (JSON puro, sem markdown):
{{
  "goal": "Descrição clara do tema e objetivo da busca enriquecida",
  "allow_domains": [
    "dominio1.com",
    "dominio2.org",
    "subdominio.exemplo.com"
  ],
  "queries": [
    {{
      "q": "query específica do conteúdo",
      "why": "justificativa clara de por que essa query enriquece o documento"
    }}
  ],
  "stop": {{
    "min_approved": 10,
    "max_iterations": 3,
    "max_queries_per_iter": 4
  }},
  "quality_gates": {{
    "must_types": ["pdf", "html"],
    "max_age_years": 3,
    "min_score": 0.7,
    "min_anchor_signals": 0
  }}
}}

IMPORTANTE: 
- Não presuma que é sempre regulatório/governamental
- Analise o CONTEÚDO real e sugira as melhores fontes PARA AQUELE ASSUNTO
- Seja específico e relevante ao tema identificado

Responda APENAS com o JSON, sem explicações adicionais ou markdown."""

        try:
            # Call LLM (use existing LLM client infrastructure)
            response_text = self._call_llm_raw(prompt)
            
            # Parse JSON response
            plan_dict = self._extract_json_from_response(response_text)
            
            # Validate and return
            return AllowlistPlan(**plan_dict)
        
        except Exception as e:
            logger.error("allowlist_plan_llm_failed", error=str(e))
            # Return default plan on failure
            return self._default_plan()
    
    def _call_llm_raw(self, prompt: str) -> str:
        """
        Call LLM with raw prompt.
        
        Args:
            prompt: Full prompt text
            
        Returns:
            LLM response text
        """
        # Check if real LLM is available
        use_real_llm = os.getenv("USE_REAL_GPT_ALLOWLIST", "false").lower() == "true"
        
        if not use_real_llm or not hasattr(self.llm, '_call_chat_completion'):
            logger.info("allowlist_llm_placeholder", msg="Using placeholder (set USE_REAL_GPT_ALLOWLIST=true)")
        else:
            # Use REAL OpenAI API call
            try:
                logger.info("allowlist_calling_real_gpt", model=self.llm.model)
                
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert in information retrieval and source curation. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                response = self.llm._call_chat_completion(
                    messages=messages,
                    response_format={"type": "json_object"}
                )
                
                logger.info("allowlist_gpt_response_received", response_len=len(response))
                
                return response
            
            except Exception as e:
                logger.error("allowlist_gpt_call_failed", error=str(e), msg="Falling back to placeholder")
                # Continue to placeholder below
        
        # Return placeholder plan (adaptativo baseado no contexto)
        # Tenta detectar o domínio do documento no prompt
        prompt_lower = prompt.lower()
        
        # Detecção simples de domínio
        if any(word in prompt_lower for word in ["production", "rag", "llm", "embedding", "vector"]):
            # Documento técnico sobre AI/ML
            return json.dumps({
                "goal": "Enriquecimento sobre RAG, LLMs e sistemas de produção",
                "allow_domains": [
                    "arxiv.org",
                    "openai.com",
                    "huggingface.co",
                    "github.com",
                    "python.langchain.com",
                    "docs.llamaindex.ai",
                    "www.anthropic.com",
                    "cloud.google.com",
                    "learn.microsoft.com",
                    "aws.amazon.com"
                ],
                "queries": [
                    {
                        "q": "site:arxiv.org RAG production deployment",
                        "why": "Buscar papers científicos sobre deployment de RAG em produção"
                    },
                    {
                        "q": "LLM production best practices documentation",
                        "why": "Encontrar guias oficiais de implementação"
                    },
                    {
                        "q": "vector database optimization benchmarks",
                        "why": "Estudos comparativos de performance de bancos vetoriais"
                    }
                ],
                "stop": {
                    "min_approved": 10,
                    "max_iterations": 3,
                    "max_queries_per_iter": 4
                },
                "quality_gates": {
                    "must_types": ["pdf", "html"],
                    "max_age_years": 2,
                    "min_score": 0.7,
                    "min_anchor_signals": 0
                }
            })
        
        elif any(word in prompt_lower for word in ["saúde", "ans", "plano", "regulament"]):
            # Documento regulatório de saúde
            return json.dumps({
                "goal": "Regulamentação no setor de saúde suplementar",
                "allow_domains": [
                    "ans.gov.br",
                    "gov.br",
                    "planalto.gov.br",
                    "saude.gov.br",
                    "anvisa.gov.br",
                ],
                "queries": [
                    {
                        "q": "regulamentação saúde suplementar ANS",
                        "why": "Buscar normas e resoluções da ANS sobre o setor"
                    }
                ],
                "stop": {
                    "min_approved": 10,
                    "max_iterations": 3,
                    "max_queries_per_iter": 4
                },
                "quality_gates": {
                    "must_types": ["pdf", "html"],
                    "max_age_years": 3,
                    "min_score": 0.7,
                    "min_anchor_signals": 0
                }
            })
        
        else:
            # Genérico: busca acadêmica/técnica
            return json.dumps({
                "goal": "Enriquecimento com fontes confiáveis sobre o tema do documento",
                "allow_domains": [
                    "wikipedia.org",
                    "arxiv.org",
                    "scholar.google.com",
                    "researchgate.net",
                    "*.edu",
                    "*.ac.uk",
                ],
                "queries": [
                    {
                        "q": "definitive guide comprehensive study",
                        "why": "Buscar guias abrangentes e estudos completos sobre o tema"
                    }
                ],
                "stop": {
                    "min_approved": 10,
                    "max_iterations": 3,
                    "max_queries_per_iter": 4
                },
                "quality_gates": {
                    "must_types": ["pdf", "html"],
                    "max_age_years": 3,
                    "min_score": 0.7,
                    "min_anchor_signals": 0
                }
            })
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed JSON dict
        """
        # Try to extract JSON from markdown code blocks or raw text
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(lines[1:-1])
        
        # Parse JSON
        return json.loads(response)
    
    def _default_plan(self) -> AllowlistPlan:
        """
        Return default fallback plan.
        
        Returns:
            Default AllowlistPlan
        """
        return AllowlistPlan(
            goal="Enriquecimento de documentos regulatórios",
            allow_domains=["gov.br", "planalto.gov.br"],
            queries=[
                {"q": "regulamentação brasil", "why": "Busca genérica"}
            ],
            stop={
                "min_approved": 10,
                "max_iterations": 3,
                "max_queries_per_iter": 4
            },
            quality_gates={
                "must_types": ["pdf", "html"],
                "max_age_years": 3,
                "min_score": 0.7,
                "min_anchor_signals": 0
            }
        )

