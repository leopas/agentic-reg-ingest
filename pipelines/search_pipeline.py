# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Search pipeline: CSE → score → rank → persist."""

import argparse
import hashlib
import structlog
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agentic.cse_client import CSEClient
from agentic.detect import detect_type, _url_ext
from agentic.normalize import extract_domain, normalize_url
from agentic.scoring import ResultScorer
from common.env_readers import load_yaml_with_env
from db.dao import DocumentCatalogDAO, SearchQueryDAO, SearchResultDAO
from db.session import DatabaseSession

# Load .env into os.environ
load_dotenv()

logger = structlog.get_logger()


class SearchPipeline:
    """Execute search pipeline: CSE → rank → cache."""
    
    def __init__(self, cse_config: Dict[str, Any], db_config: Dict[str, Any]):
        """
        Initialize search pipeline.
        
        Args:
            cse_config: CSE configuration from cse.yaml
            db_config: DB configuration from db.yaml
        """
        self.cse_config = cse_config
        self.db_config = db_config
        
        # Initialize clients
        self.cse = CSEClient(
            api_key=cse_config["api_key"],
            cx=cse_config["cx"],
            timeout=int(cse_config["timeout_seconds"]),
        )
        
        self.scorer = ResultScorer(cse_config)
        self.db_session = DatabaseSession()
        self.ttl_days = int(db_config.get("ttl_days", 7))
    
    def build_cache_key(
        self,
        cx: str,
        query: str,
        allow_domains: Optional[List[str]],
        topn: int,
    ) -> str:
        """Build cache key from search parameters."""
        allow_str = "|".join(sorted(allow_domains or []))
        cache_str = f"{cx}|{query}|{allow_str}|{topn}"
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get content metadata via HEAD request with typing detection.
        
        Args:
            url: Document URL
            
        Returns:
            Dict with content_type, last_modified, headers, and typing info
        """
        try:
            response = requests.head(
                url,
                timeout=int(self.cse_config["timeout_seconds"]),
                allow_redirects=True,
            )
            
            content_type = response.headers.get("Content-Type")
            last_modified_str = response.headers.get("Last-Modified")
            
            last_modified = None
            if last_modified_str:
                try:
                    last_modified = datetime.strptime(
                        last_modified_str,
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                except Exception:
                    pass
            
            # Detect document type
            typing_info = detect_type(url, dict(response.headers), sniff_magic=True)
            
            logger.debug(
                "metadata_fetched",
                url=url,
                final_type=typing_info.get("final_type"),
                fetch_status=typing_info.get("fetch_status"),
            )
            
            return {
                "content_type": content_type,
                "last_modified": last_modified,
                "headers": dict(response.headers),
                "typing": typing_info,
            }
        
        except Exception as e:
            logger.warning("metadata_fetch_failed", url=url, error=str(e))
            # Still try to detect from URL alone
            typing_info = detect_type(url, {}, sniff_magic=False)
            typing_info["fetch_status"] = "error"
            
            return {
                "content_type": None,
                "last_modified": None,
                "headers": {},
                "typing": typing_info,
            }
    
    def execute(
        self,
        query: str,
        allow_domains: Optional[List[str]] = None,
        topn: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Execute search pipeline.
        
        Args:
            query: Search query
            allow_domains: Optional domain whitelist
            topn: Max results to retrieve
            
        Returns:
            List of approved search results
        """
        cx = self.cse_config["cx"]
        cache_key = self.build_cache_key(cx, query, allow_domains, topn)
        
        logger.info("search_pipeline_start", query=query, cache_key=cache_key)
        
        # Check cache
        with next(self.db_session.get_session()) as session:
            cached_query = SearchQueryDAO.find_by_cache_key(session, cache_key)
            
            if cached_query and SearchQueryDAO.is_cache_valid(cached_query):
                logger.info("cache_hit", cache_key=cache_key)
                approved = SearchResultDAO.get_approved_results(session, cached_query.id)
                
                return [
                    {
                        "url": r.url,
                        "title": r.title,
                        "snippet": r.snippet,
                        "score": float(r.score) if r.score else 0.0,
                        "content_type": r.content_type,
                    }
                    for r in approved
                ]
            
            logger.info("cache_miss", cache_key=cache_key)
            
            # Execute CSE search
            items = self.cse.search_all(
                query=query,
                max_results=topn,
                results_per_page=int(self.cse_config["results_per_page"]),
            )
            
            logger.info("cse_results", count=len(items))
            
            # Score and rank
            scored_results = []
            
            for idx, item in enumerate(items):
                url = item.get("link", "")
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                
                # Normalize URL
                canonical_url = normalize_url(url)
                
                # Get metadata
                metadata = self.get_metadata(canonical_url)
                
                # Score
                score = self.scorer.score(
                    url=canonical_url,
                    title=title,
                    snippet=snippet,
                    content_type=metadata["content_type"],
                    last_modified=metadata["last_modified"],
                )
                
                typing_info = metadata.get("typing", {})
                headers = metadata.get("headers", {})
                
                scored_results.append({
                    "url": canonical_url,
                    "title": title,
                    "snippet": snippet,
                    "rank_position": idx + 1,
                    "score": score,
                    "content_type": metadata["content_type"],
                    "last_modified": metadata["last_modified"],
                    # Typing fields
                    "http_content_type": headers.get("Content-Type"),
                    "http_content_disposition": headers.get("Content-Disposition"),
                    "url_ext": _url_ext(canonical_url),
                    "detected_mime": typing_info.get("detected_mime"),
                    "detected_ext": typing_info.get("detected_ext"),
                    "final_type": typing_info.get("final_type", "unknown"),
                    "fetch_status": typing_info.get("fetch_status"),
                })
            
            # Sort by score descending
            scored_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Persist to database
            self._persist_results(session, cache_key, cx, query, allow_domains, topn, scored_results)
            
            logger.info("search_pipeline_complete", results_count=len(scored_results))
            
            return scored_results
    
    def _persist_results(
        self,
        session: Session,
        cache_key: str,
        cx: str,
        query: str,
        allow_domains: Optional[List[str]],
        topn: int,
        results: List[Dict[str, Any]],
    ) -> None:
        """Persist search results to database."""
        # Create/update search_query
        allow_str = "|".join(allow_domains) if allow_domains else None
        
        query_record = SearchQueryDAO.create(
            session,
            cache_key=cache_key,
            cx=cx,
            query_text=query,
            allow_domains=allow_str,
            top_n=topn,
            ttl_days=self.ttl_days,
        )
        
        # Create search_result records
        for result in results:
            SearchResultDAO.create(
                session,
                query_id=query_record.id,
                url=result["url"],
                title=result["title"],
                snippet=result["snippet"],
                rank_position=result["rank_position"],
                score=result["score"],
                content_type=result["content_type"],
                last_modified=result["last_modified"],
                approved=True,
                # Typing fields
                http_content_type=result.get("http_content_type"),
                http_content_disposition=result.get("http_content_disposition"),
                url_ext=result.get("url_ext"),
                detected_mime=result.get("detected_mime"),
                detected_ext=result.get("detected_ext"),
                final_type=result.get("final_type", "unknown"),
                fetch_status=result.get("fetch_status"),
            )
            
            # Upsert document_catalog
            domain = extract_domain(result["url"])
            
            DocumentCatalogDAO.upsert(
                session,
                canonical_url=result["url"],
                content_type=result["content_type"],
                last_modified=result["last_modified"],
                title=result["title"],
                domain=domain,
                final_type=result.get("final_type", "unknown"),
            )
        
        session.commit()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Run search pipeline")
    parser.add_argument("--config", default="configs/cse.yaml", help="CSE config path")
    parser.add_argument("--db", default="configs/db.yaml", help="DB config path")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--topn", type=int, default=100, help="Max results")
    
    args = parser.parse_args()
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    
    # Load configs
    cse_config = load_yaml_with_env(args.config)
    db_config = load_yaml_with_env(args.db)
    
    # Run pipeline
    pipeline = SearchPipeline(cse_config, db_config)
    results = pipeline.execute(query=args.query, topn=args.topn)
    
    print(f"Found {len(results)} results")
    for r in results[:10]:
        print(f"  [{r['score']:.2f}] {r['title']}")


if __name__ == "__main__":
    main()

