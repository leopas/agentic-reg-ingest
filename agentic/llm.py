# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""LLM wrapper for intelligent routing and PDF analysis."""

import json
import structlog
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

if TYPE_CHECKING:
    from agentic.schemas import CandidateSummary, JudgeResponse, Plan

logger = structlog.get_logger()


class LLMClient:
    """OpenAI LLM client for agentic tasks."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        max_tokens: int = 2000,
        timeout: int = 30,
    ):
        """
        Initialize LLM client.
        
        Args:
            api_key: OpenAI API key
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max response tokens
            timeout: Request timeout
        """
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def _call_chat_completion(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Call OpenAI chat completion API.
        
        Args:
            messages: List of chat messages
            response_format: Optional response format spec
            
        Returns:
            Response content string
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
    
    def suggest_pdf_markers(
        self,
        title: str,
        pages_preview: List[str],
        domain: str,
    ) -> List[Dict[str, Any]]:
        """
        Suggest anchoring markers for PDF chunking.
        
        Args:
            title: Document title
            pages_preview: Preview text from first few pages
            domain: Source domain
            
        Returns:
            List of marker suggestions with type and patterns
            Example: [
                {"type": "article", "pattern": "Art\\. \\d+"},
                {"type": "chapter", "pattern": "CAPÍTULO [IVX]+"},
                {"type": "annex", "pattern": "ANEXO [IVX]+"},
            ]
        """
        preview_text = "\n---\n".join(pages_preview[:5])
        
        prompt = f"""You are analyzing a regulatory document from {domain}.

Title: {title}

First pages preview:
{preview_text}

Suggest anchoring markers to guide intelligent chunking. Return a JSON array of markers.

Each marker should have:
- "type": one of "article", "chapter", "section", "annex", "table", "page_range"
- "pattern": regex pattern to detect this marker
- "confidence": 0.0-1.0

Example:
[
  {{"type": "article", "pattern": "Art\\\\. \\\\d+", "confidence": 0.9}},
  {{"type": "annex", "pattern": "ANEXO [IVX]+", "confidence": 0.8}}
]

Return only valid JSON array, no explanation."""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that returns valid JSON."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            # OpenAI json_object mode wraps array in object, extract it
            parsed = json.loads(response)
            
            # Handle different response structures
            if isinstance(parsed, list):
                markers = parsed
            elif "markers" in parsed:
                markers = parsed["markers"]
            elif "suggestions" in parsed:
                markers = parsed["suggestions"]
            else:
                # Fallback: use first list found
                for value in parsed.values():
                    if isinstance(value, list):
                        markers = value
                        break
                else:
                    markers = []
            
            return markers
        
        except Exception:
            # Fallback to default markers
            return [
                {"type": "article", "pattern": r"Art\. \d+", "confidence": 0.5},
                {"type": "chapter", "pattern": r"CAP[ÍI]TULO [IVX]+", "confidence": 0.5},
            ]
    
    def route_fallback(
        self,
        title: str,
        snippet: str,
        url: str,
    ) -> Literal["pdf", "zip", "html"]:
        """
        Fallback routing when content-type is ambiguous.
        
        Args:
            title: Document title
            snippet: Search snippet
            url: Document URL
            
        Returns:
            Document type: 'pdf', 'zip', or 'html'
        """
        prompt = f"""Based on the following information, determine the document type.

Title: {title}
Snippet: {snippet}
URL: {url}

Return ONLY one word: "pdf", "zip", or "html"."""
        
        messages = [
            {"role": "system", "content": "You return only one word: pdf, zip, or html."},
            {"role": "user", "content": prompt},
        ]
        
        try:
            response = self._call_chat_completion(messages)
            response_lower = response.strip().lower()
            
            if "pdf" in response_lower:
                return "pdf"
            elif "zip" in response_lower:
                return "zip"
            else:
                return "html"
        
        except Exception:
            # Default fallback
            if url.lower().endswith('.pdf'):
                return "pdf"
            elif url.lower().endswith('.zip'):
                return "zip"
            else:
                return "html"
    
    def extract_html_structure(
        self,
        base_url: str,
        excerpt: str,
        max_chars_llm: int = 80000,
    ) -> Dict[str, Any]:
        """
        Extract structure from HTML content using LLM.
        
        This does NOT summarize - it STRUCTURES the content by identifying
        sections, headings, tables, and anchors for intelligent chunking.
        
        Args:
            base_url: Source URL
            excerpt: HTML text excerpt (already cleaned)
            max_chars_llm: Maximum characters to send to LLM
            
        Returns:
            Dictionary with:
            {
                "title": str | null,
                "language": "pt" | "en" | ...,
                "sections": [{"heading": str, "text": str}],
                "tables": [{"caption": str, "rows": int | null}],
                "pdf_links": [str],
                "anchors": [{"type": "h1|h2|h3|h4|table|page", "value": str, "hint": str | null}]
            }
        """
        # Truncate excerpt if too long
        if len(excerpt) > max_chars_llm:
            excerpt = excerpt[:max_chars_llm] + "\n\n[...truncated...]"
        
        system_prompt = """Você extrai estrutura de documentos HTML regulatórios (ANS/Planalto/ANPD/BACEN/CVM).

IMPORTANTE:
- Responda APENAS com JSON válido
- NÃO resuma o conteúdo - preserve seções na ordem original
- NÃO invente links ou informações
- Use o schema exato especificado

Campos obrigatórios:
{
  "title": string ou null,
  "language": "pt" | "en" | "es" | "other",
  "sections": [{"heading": string, "text": string}],
  "tables": [{"caption": string, "rows": number ou null}],
  "pdf_links": [string],
  "anchors": [{"type": "h1|h2|h3|h4|table|page", "value": string, "hint": string ou null}]
}

Regras:
- 'sections' preserva a ordem do texto principal com headings
- 'anchors' lista h1..h4 e 'table' com nomes/títulos aparentes
- Use 'page' em anchors apenas se não houver headings
- Evite repetir conteúdo entre seções
- Nunca invente links ou dados"""

        user_prompt = json.dumps({
            "base_url": base_url,
            "html_excerpt": excerpt,
        }, ensure_ascii=False)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            logger.info("llm_html_struct_start", url=base_url, excerpt_len=len(excerpt))
            
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            structure = json.loads(response)
            
            # Validate and fill missing fields
            result = {
                "title": structure.get("title"),
                "language": structure.get("language", "pt"),
                "sections": structure.get("sections", []),
                "tables": structure.get("tables", []),
                "pdf_links": structure.get("pdf_links", []),
                "anchors": structure.get("anchors", []),
            }
            
            logger.info(
                "llm_html_struct_done",
                url=base_url,
                sections_count=len(result["sections"]),
                tables_count=len(result["tables"]),
                anchors_count=len(result["anchors"]),
            )
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error("llm_html_struct_json_error", url=base_url, error=str(e))
            # Return minimal schema
            return {
                "title": None,
                "language": "pt",
                "sections": [],
                "tables": [],
                "pdf_links": [],
                "anchors": [],
            }
        
        except Exception as e:
            logger.error("llm_html_struct_failed", url=base_url, error=str(e))
            # Return minimal schema
            return {
                "title": None,
                "language": "pt",
                "sections": [],
                "tables": [],
                "pdf_links": [],
                "anchors": [],
            }
    
    def plan_from_prompt(self, user_prompt: str) -> "Plan":
        """
        Generate agentic search plan from natural language prompt.
        
        Args:
            user_prompt: User's search goal in natural language
            
        Returns:
            Validated Plan object
        """
        system_prompt = """Você é um planejador de busca regulatória em saúde suplementar (ANS/Planalto/ANPD/BACEN/CVM).

IMPORTANTE:
- Gere um PLANO JSON estrito – nada de prosa
- Objetivo: maximizar fontes oficiais citáveis (PDF/ZIP) e minimizar ruído
- Inclua queries (com 'k'), allowlist, stop conditions e quality gates
- Use linguagem portuguesa para termos, mas os campos JSON em inglês

Schema obrigatório:
{
  "goal": string (objetivo da busca),
  "topics": [string] (tópicos principais),
  "queries": [{"q": string, "why": string (justificativa OBRIGATÓRIA), "k": int (1-10)}],
  "allow_domains": [string] (ex: ["www.gov.br", "www.planalto.gov.br"]),
  "deny_patterns": [string] (regex patterns para excluir),
  "stop": {
    "min_approved": int (mínimo de documentos aprovados),
    "max_iterations": int (máximo de iterações),
    "max_queries_per_iter": int (queries por iteração)
  },
  "quality_gates": {
    "must_types": [string] (ex: ["pdf","zip"]),
    "max_age_years": int,
    "min_anchor_signals": int,
    "min_score": float (0.0-1.0)
  },
  "budget": {
    "max_cse_calls": int,
    "ttl_days": int
  }
}

Dicas:
- Para ANS: use "www.gov.br/ans" no allowlist
- Para Planalto: use "www.planalto.gov.br"
- Queries devem ser específicas (ex: "RN 395 ANS", "Resolução Normativa")
- k entre 5-10 por query
- must_types: ["pdf","zip"] para documentos oficiais, ["html"] para páginas, ou ["pdf","zip","html"] para tudo
- Campo 'why' em TODAS as queries é OBRIGATÓRIO: explique o propósito (ex: "Buscar normas base", "Completar com anexos específicos")

VALORES RECOMENDADOS para quality_gates:
- min_anchor_signals: 0 para HTML (páginas sem estrutura), 1 para PDFs/ZIPs
- min_score: entre 1.5 (permissivo) e 2.5 (rigoroso) na escala 0-5
- max_age_years: 3-5 anos é razoável
- must_types: ["html"] OU ["pdf","zip"] OU ["pdf","zip","html"] dependendo do objetivo"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            logger.info("llm_plan_start", prompt_len=len(user_prompt))
            
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            plan_dict = json.loads(response)
            
            # Post-process: ensure 'why' is never null and fix unreasonable values
            if "queries" in plan_dict:
                for query in plan_dict["queries"]:
                    if query.get("why") is None or not query.get("why"):
                        # Generate default 'why' from query text
                        query["why"] = f"Busca relevante: {query.get('q', 'query')[:50]}"
            
            # Post-process: fix unreasonable quality_gates values
            if "quality_gates" in plan_dict:
                qg = plan_dict["quality_gates"]
                
                # If min_anchor_signals too high for HTML searches, adjust
                if "html" in qg.get("must_types", []):
                    if qg.get("min_anchor_signals", 0) > 1:
                        logger.warning(
                            "llm_plan_anchor_adjusted",
                            original=qg.get("min_anchor_signals"),
                            new=0,
                            reason="HTML searches don't have anchors"
                        )
                        qg["min_anchor_signals"] = 0
                
                # Ensure min_score is reasonable (0-5 scale)
                if qg.get("min_score", 0) > 4.0:
                    logger.warning(
                        "llm_plan_score_adjusted",
                        original=qg.get("min_score"),
                        new=2.5,
                        reason="min_score too high"
                    )
                    qg["min_score"] = 2.5
            
            # Import here to avoid circular dependency
            from agentic.schemas import Plan
            
            # Validate and construct Plan
            plan = Plan(**plan_dict)
            
            logger.info(
                "llm_plan_done",
                queries_count=len(plan.queries),
                min_approved=plan.stop.min_approved,
                must_types=plan.quality_gates.must_types,
            )
            
            return plan
        
        except json.JSONDecodeError as e:
            logger.error("llm_plan_json_error", error=str(e))
            raise ValueError(f"Failed to parse plan JSON: {e}")
        
        except Exception as e:
            logger.error("llm_plan_failed", error=str(e))
            raise
    
    def judge_candidates(
        self,
        plan: "Plan",
        candidates: List["CandidateSummary"],
    ) -> "JudgeResponse":
        """
        Judge search candidates and propose new queries.
        
        Args:
            plan: Search plan with quality gates
            candidates: List of candidate summaries to judge
            
        Returns:
            JudgeResponse with approved_urls, rejected, and new_queries
        """
        system_prompt = """Você é um crítico rigoroso de fontes regulatórias.

TAREFA:
Recebe candidatos (título/url/snippet/headers/score/final_type/anchor_signals) e um Plan (quality_gates).
Devolva JSON estrito com:
{
  "approved_urls": [string],
  "rejected": [{"url": string, "reason": string, "violations": [string]}],
  "new_queries": [string]
}

CRITÉRIOS DE REJEIÇÃO:
- Wrappers HTML (páginas que só linkam para PDF)
- Blogs, notícias, ou fontes não-oficiais
- Documentos desatualizados
- Baixa relevância ao objetivo
- Falta de marcadores estruturais (Art., Anexo, Tabela)

SUGESTÕES DE QUERIES:
- Se faltam anexos específicos, sugira "Anexo X RN Y"
- Se faltam tabelas, sugira "Tabela TUSS" ou similar
- Se faltam resoluções, sugira "RN [número]"
- Máximo 3 novas queries por iteração

IMPORTANTE:
- Apenas URLs em approved_urls que realmente atendem aos quality_gates
- Seja conservador: na dúvida, rejeite
- Reasons devem ser específicas e em português"""

        # Prepare user content
        user_content = {
            "plan_goal": plan.goal,
            "quality_gates": {
                "must_types": plan.quality_gates.must_types,
                "max_age_years": plan.quality_gates.max_age_years,
                "min_anchor_signals": plan.quality_gates.min_anchor_signals,
                "min_score": plan.quality_gates.min_score,
            },
            "candidates": [
                {
                    "url": c.url,
                    "title": c.title,
                    "snippet": c.snippet,
                    "score": c.score,
                    "final_type": c.final_type,
                    "anchor_signals": c.anchor_signals,
                    "last_modified": c.headers.get("Last-Modified"),
                }
                for c in candidates
            ],
        }
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_content, ensure_ascii=False)},
        ]
        
        try:
            logger.info("llm_judge_start", candidates_count=len(candidates))
            
            response = self._call_chat_completion(
                messages,
                response_format={"type": "json_object"},
            )
            
            judge_dict = json.loads(response)
            
            # Import here to avoid circular dependency
            from agentic.schemas import JudgeResponse, RejectedSummary
            
            # Ensure rejected has proper structure
            rejected_list = []
            for r in judge_dict.get("rejected", []):
                if isinstance(r, dict):
                    rejected_list.append(RejectedSummary(**r))
                else:
                    # Fallback if LLM didn't follow schema
                    rejected_list.append(RejectedSummary(
                        url=str(r),
                        reason="Rejected by judge",
                        violations=[],
                    ))
            
            judge_response = JudgeResponse(
                approved_urls=judge_dict.get("approved_urls", []),
                rejected=rejected_list,
                new_queries=judge_dict.get("new_queries", []),
            )
            
            logger.info(
                "llm_judge_done",
                approved_count=len(judge_response.approved_urls),
                rejected_count=len(judge_response.rejected),
                new_queries_count=len(judge_response.new_queries),
            )
            
            return judge_response
        
        except json.JSONDecodeError as e:
            logger.error("llm_judge_json_error", error=str(e))
            # Return safe fallback
            from agentic.schemas import JudgeResponse
            return JudgeResponse(approved_urls=[], rejected=[], new_queries=[])
        
        except Exception as e:
            logger.error("llm_judge_failed", error=str(e))
            # Return safe fallback
            from agentic.schemas import JudgeResponse
            return JudgeResponse(approved_urls=[], rejected=[], new_queries=[])

