# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Agentic Search Controller: Plan→Act→Observe→Judge→Re-plan loop."""

import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, List

import structlog
import requests
from sqlalchemy.orm import Session

from agentic.cse_client import CSEClient
from agentic.detect import detect_type, _url_ext
from agentic.llm import LLMClient
from agentic.normalize import extract_domain, normalize_url
from agentic.quality import apply_quality_gates, count_anchor_signals
from agentic.schemas import (
    AgenticResult,
    CandidateSummary,
    Plan,
    RejectedSummary,
)
from agentic.scoring import ResultScorer
from db.dao import AgenticIterDAO, AgenticPlanDAO, DocumentCatalogDAO, SearchQueryDAO, SearchResultDAO

logger = structlog.get_logger()


class AgenticSearchController:
    """Controller for agentic search with Plan→Act→Observe→Judge→Re-plan loop."""
    
    def __init__(
        self,
        cse_client: CSEClient,
        llm_client: LLMClient,
        scorer: ResultScorer,
        timeout: int = 20,
    ):
        """
        Initialize agentic controller.
        
        Args:
            cse_client: Google CSE client
            llm_client: LLM client for planning and judging
            scorer: Result scorer
            timeout: HTTP timeout for metadata fetching
        """
        self.cse = cse_client
        self.llm = llm_client
        self.scorer = scorer
        self.timeout = timeout
    
    def run_agentic_search(
        self,
        plan: Plan,
        session: Session,
    ) -> AgenticResult:
        """
        Execute agentic search loop.
        
        Steps per iteration:
        1. Select queries (up to max_queries_per_iter)
        2. ACT: Execute CSE searches
        3. OBSERVE: Fetch metadata, detect types, score candidates
        4. JUDGE: Apply quality gates + LLM judgment
        5. PERSIST: Save iteration results
        6. CHECK STOP CONDITIONS
        7. RE-PLAN: Merge new queries
        
        Args:
            plan: Search plan
            session: Database session
            
        Returns:
            AgenticResult with stats and promoted URLs
        """
        plan_id = str(uuid.uuid4())
        
        logger.info(
            "agentic_search_start",
            plan_id=plan_id,
            goal=plan.goal,
            queries_count=len(plan.queries),
        )
        
        # Save plan to DB
        AgenticPlanDAO.save_plan(
            session,
            plan_id=plan_id,
            goal=plan.goal,
            plan_json=plan.dict(),
        )
        session.commit()
        
        # Initialize tracking
        all_approved_urls = set()
        all_approved_candidates = []
        executed_queries_total = set()
        pending_queries = [q.q for q in plan.queries]
        cse_calls_count = 0
        
        # Main agentic loop
        for iteration in range(1, plan.stop.max_iterations + 1):
            logger.info("agentic_iteration_start", iteration=iteration, plan_id=plan_id)
            
            # STEP 1: Select queries for this iteration
            queries_this_iter = pending_queries[:plan.stop.max_queries_per_iter]
            
            if not queries_this_iter:
                logger.info("agentic_no_queries", iteration=iteration)
                result = AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration - 1,
                    approved_total=len(all_approved_urls),
                    stopped_by="no_queries",
                    promoted_urls=list(all_approved_urls),
                )
                return result
            
            # STEP 2: ACT - Execute CSE searches
            all_candidates = []
            
            for query in queries_this_iter:
                # Check budget
                if cse_calls_count >= plan.budget.max_cse_calls:
                    logger.warning("agentic_budget_exceeded", calls=cse_calls_count)
                    break
                
                logger.info("agentic_cse_query", query=query)
                
                try:
                    # Get k results for this query
                    query_spec = next((q for q in plan.queries if q.q == query), None)
                    k = query_spec.k if query_spec else 10
                    
                    items = self.cse.search_all(
                        query=query,
                        max_results=k,
                        results_per_page=10,
                    )
                    
                    cse_calls_count += 1
                    
                    logger.info("agentic_cse_results", query=query, count=len(items))
                    
                    # STEP 3: OBSERVE - Process each hit
                    for item in items:
                        url = normalize_url(item.get("link", ""))
                        
                        # Skip if already approved
                        if url in all_approved_urls:
                            continue
                        
                        # Check deny patterns
                        if self._matches_deny_pattern(url, plan.deny_patterns):
                            logger.debug("agentic_denied_pattern", url=url)
                            continue
                        
                        # Check allow domains
                        if plan.allow_domains and not self._matches_allow_domains(url, plan.allow_domains):
                            logger.debug("agentic_not_in_allowlist", url=url)
                            continue
                        
                        # Fetch metadata
                        candidate = self._build_candidate(url, item, plan)
                        
                        if candidate:
                            all_candidates.append(candidate)
                
                except Exception as e:
                    logger.error("agentic_cse_error", query=query, error=str(e))
                    continue
            
            executed_queries_total.update(queries_this_iter)
            
            logger.info(
                "agentic_observe_done",
                iteration=iteration,
                candidates_count=len(all_candidates),
            )
            
            # STEP 4: JUDGE - Apply quality gates + LLM
            approved_this_iter = []
            rejected_this_iter = []
            
            # 4a. Hard quality gates (code-level)
            filtered_candidates = []
            for candidate in all_candidates:
                passed, violations = apply_quality_gates(plan.quality_gates, candidate)
                
                if passed:
                    filtered_candidates.append(candidate)
                else:
                    rejected_this_iter.append(RejectedSummary(
                        url=candidate.url,
                        reason="Quality gates failed",
                        violations=violations,
                    ))
            
            logger.info(
                "agentic_quality_gates_applied",
                iteration=iteration,
                passed=len(filtered_candidates),
                rejected=len(rejected_this_iter),
            )
            
            # 4b. LLM judge (semantic)
            if filtered_candidates:
                judge_response = self.llm.judge_candidates(plan, filtered_candidates)
                
                # Collect approved
                for url in judge_response.approved_urls:
                    # Find candidate
                    cand = next((c for c in filtered_candidates if c.url == url), None)
                    if cand and url not in all_approved_urls:
                        approved_this_iter.append(cand)
                        all_approved_urls.add(url)
                        all_approved_candidates.append(cand)
                
                # Collect LLM rejections
                rejected_this_iter.extend(judge_response.rejected)
                
                new_queries = judge_response.new_queries[:3]  # Cap at 3
            else:
                new_queries = []
            
            logger.info(
                "agentic_judge_done",
                iteration=iteration,
                approved=len(approved_this_iter),
                rejected=len(rejected_this_iter),
                new_queries=len(new_queries),
            )
            
            # STEP 5: PERSIST - Save iteration
            try:
                AgenticIterDAO.save_iter(
                    session,
                    plan_id=plan_id,
                    iter_num=iteration,
                    executed_queries=queries_this_iter,
                    approved_urls=[c.url for c in approved_this_iter],
                    rejected_json=[r.dict() for r in rejected_this_iter],
                    new_queries=new_queries,
                    summary=f"Iter {iteration}: {len(approved_this_iter)} approved, {len(rejected_this_iter)} rejected",
                )
                
                # Persist approved to search_result
                self._persist_approved(session, plan, approved_this_iter)
                
                session.commit()
            
            except Exception as e:
                logger.error("agentic_persist_failed", iteration=iteration, error=str(e))
                session.rollback()
                # Continue to next iteration despite persistence error
            
            logger.info(
                "agentic_iteration_complete",
                iteration=iteration,
                total_approved=len(all_approved_urls),
            )
            
            # STEP 6: CHECK STOP CONDITIONS
            
            # 6a. Minimum approved reached
            if len(all_approved_urls) >= plan.stop.min_approved:
                logger.info(
                    "agentic_stop_min_approved",
                    approved=len(all_approved_urls),
                    target=plan.stop.min_approved,
                )
                return AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration,
                    approved_total=len(all_approved_urls),
                    stopped_by="min_approved",
                    promoted_urls=list(all_approved_urls),
                )
            
            # 6b. Budget exceeded
            if cse_calls_count >= plan.budget.max_cse_calls:
                logger.info("agentic_stop_budget", calls=cse_calls_count)
                return AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration,
                    approved_total=len(all_approved_urls),
                    stopped_by="budget",
                    promoted_urls=list(all_approved_urls),
                )
            
            # 6c. No progress (no approvals and no new queries)
            if not approved_this_iter and not new_queries:
                logger.info("agentic_stop_no_progress", iteration=iteration)
                return AgenticResult(
                    plan_id=plan_id,
                    iterations=iteration,
                    approved_total=len(all_approved_urls),
                    stopped_by="no_progress",
                    promoted_urls=list(all_approved_urls),
                )
            
            # STEP 7: RE-PLAN - Merge new queries
            pending_queries = [q for q in pending_queries if q not in queries_this_iter]
            pending_queries.extend(new_queries)
            
            # Dedup while preserving order
            seen = set()
            deduped = []
            for q in pending_queries:
                if q not in seen:
                    seen.add(q)
                    deduped.append(q)
            pending_queries = deduped
            
            logger.info(
                "agentic_replan",
                iteration=iteration,
                pending_queries=len(pending_queries),
                new_queries_added=len(new_queries),
            )
        
        # Reached max iterations
        logger.info("agentic_stop_max_iterations", iterations=plan.stop.max_iterations)
        return AgenticResult(
            plan_id=plan_id,
            iterations=plan.stop.max_iterations,
            approved_total=len(all_approved_urls),
            stopped_by="max_iterations",
            promoted_urls=list(all_approved_urls),
        )
    
    def _build_candidate(
        self,
        url: str,
        cse_item: Dict[str, Any],
        plan: Plan,
    ) -> CandidateSummary | None:
        """
        Build candidate summary from CSE item with metadata.
        
        Args:
            url: Normalized URL
            cse_item: CSE search result item
            plan: Search plan
            
        Returns:
            CandidateSummary or None if failed
        """
        try:
            title = cse_item.get("title", "")
            snippet = cse_item.get("snippet", "")
            
            # Fetch metadata via HEAD
            try:
                response = requests.head(url, timeout=self.timeout, allow_redirects=True)
                headers = dict(response.headers)
            except Exception as e:
                logger.debug("agentic_head_failed", url=url, error=str(e))
                headers = {}
            
            # Detect document type
            typing_info = detect_type(url, headers, sniff_magic=False)
            
            # Score
            content_type = headers.get("Content-Type")
            last_modified_str = headers.get("Last-Modified")
            last_modified = None
            if last_modified_str:
                try:
                    last_modified = datetime.strptime(
                        last_modified_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pass
            
            score = self.scorer.score(
                url=url,
                title=title,
                snippet=snippet,
                content_type=content_type,
                last_modified=last_modified,
            )
            
            # Count anchor signals
            combined_text = f"{title} {snippet}"
            anchor_signals = count_anchor_signals(combined_text)
            
            candidate = CandidateSummary(
                url=url,
                title=title,
                snippet=snippet,
                headers=headers,
                score=score,
                final_type=typing_info.get("final_type", "unknown"),
                anchor_signals=anchor_signals,
            )
            
            logger.debug(
                "agentic_candidate_built",
                url=url,
                score=score,
                final_type=candidate.final_type,
                anchor_signals=anchor_signals,
            )
            
            return candidate
        
        except Exception as e:
            logger.error("agentic_candidate_error", url=url, error=str(e))
            return None
    
    def _matches_deny_pattern(self, url: str, patterns: List[str]) -> bool:
        """Check if URL matches any deny pattern."""
        import re
        
        for pattern in patterns:
            try:
                if re.search(pattern, url, re.IGNORECASE):
                    return True
            except Exception:
                continue
        return False
    
    def _matches_allow_domains(self, url: str, domains: List[str]) -> bool:
        """
        Check if URL belongs to allowed domains/paths.
        
        Supports both domain matching and path prefix matching:
        - "www.gov.br" matches any URL from www.gov.br
        - "www.gov.br/ans" matches URLs starting with www.gov.br/ans
        """
        domain = extract_domain(url)
        
        for allowed in domains:
            # Check if it's a domain-only match (no path)
            if '/' not in allowed:
                # Pure domain match
                if allowed in domain or domain.endswith(f".{allowed}"):
                    return True
            else:
                # Domain + path prefix match
                # Example: "www.gov.br/ans" should match "https://www.gov.br/ans/pt-br/..."
                if allowed in url:
                    return True
                # Also check without protocol
                url_without_protocol = url.replace("https://", "").replace("http://", "")
                if url_without_protocol.startswith(allowed):
                    return True
        
        return False
    
    def _persist_approved(
        self,
        session: Session,
        plan: Plan,
        approved: List[CandidateSummary],
    ) -> None:
        """
        Persist approved candidates to search_result and document_catalog.
        
        Args:
            session: DB session
            plan: Search plan
            approved: Approved candidates
        """
        if not approved:
            return
        
        # Create or reuse search_query record for this plan iteration
        cache_key = hashlib.sha256(plan.goal.encode()).hexdigest()
        
        # Try to find existing first
        query_record = SearchQueryDAO.find_by_cache_key(session, cache_key)
        
        if not query_record:
            # Create new only if doesn't exist
            try:
                query_record = SearchQueryDAO.create(
                    session,
                    cache_key=cache_key,
                    cx="agentic",  # Special marker
                    query_text=plan.goal,
                    allow_domains="|".join(plan.allow_domains) if plan.allow_domains else None,
                    top_n=len(approved),
                    ttl_days=plan.budget.ttl_days,
                )
            except Exception as e:
                logger.error("agentic_query_record_create_failed", error=str(e))
                # Try one more time to find (race condition)
                query_record = SearchQueryDAO.find_by_cache_key(session, cache_key)
                if not query_record:
                    logger.error("agentic_query_record_not_found")
                    return
        else:
            logger.debug("agentic_query_record_reused", cache_key=cache_key)
        
        # Create search_result records
        for idx, candidate in enumerate(approved):
            # Parse last_modified
            last_modified = None
            last_modified_str = candidate.headers.get("Last-Modified")
            if last_modified_str:
                try:
                    last_modified = datetime.strptime(
                        last_modified_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pass
            
            try:
                SearchResultDAO.create(
                    session,
                    query_id=query_record.id,
                    url=candidate.url,
                    title=candidate.title,
                    snippet=candidate.snippet,
                    rank_position=idx + 1,
                    score=candidate.score,
                    content_type=candidate.headers.get("Content-Type"),
                    last_modified=last_modified,
                    approved=True,
                    # Typing fields
                    http_content_type=candidate.headers.get("Content-Type"),
                    http_content_disposition=candidate.headers.get("Content-Disposition"),
                    url_ext=_url_ext(candidate.url),
                    detected_mime=None,  # Could enhance with detect_type full result
                    detected_ext=None,
                    final_type=candidate.final_type,
                    fetch_status="ok",
                )
            except Exception as e:
                # Could be duplicate or other error - log and continue
                logger.debug("agentic_persist_result_skipped", url=candidate.url, error=str(e)[:100])
            
            # Upsert document_catalog
            domain = extract_domain(candidate.url)
            
            try:
                DocumentCatalogDAO.upsert(
                    session,
                    canonical_url=candidate.url,
                    content_type=candidate.headers.get("Content-Type"),
                    last_modified=last_modified,
                    title=candidate.title,
                    domain=domain,
                    final_type=candidate.final_type,
                )
            except Exception as e:
                logger.debug("agentic_persist_catalog_skipped", url=candidate.url, error=str(e)[:100])
        
        session.flush()


def run_agentic_search(
    plan: Plan,
    session: Session,
    cse_client: CSEClient,
    llm_client: LLMClient,
    scorer: ResultScorer,
    timeout: int = 20,
) -> AgenticResult:
    """
    Convenience function to run agentic search.
    
    Args:
        plan: Search plan
        session: Database session
        cse_client: Google CSE client
        llm_client: LLM client
        scorer: Result scorer
        timeout: HTTP timeout
        
    Returns:
        AgenticResult
    """
    controller = AgenticSearchController(cse_client, llm_client, scorer, timeout)
    return controller.run_agentic_search(plan, session)

