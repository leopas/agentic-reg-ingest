# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Factory for search clients (CSE vs Vertex AI Search)."""

import os
from typing import Any, Dict, Union

import structlog

from agentic.cse_client import CSEClient
from agentic.vertex_search_client import VertexSearchClient

logger = structlog.get_logger()


def create_search_client(config: Dict[str, Any]) -> Union[CSEClient, VertexSearchClient]:
    """
    Create search client based on configuration.
    
    Args:
        config: Configuration dict (from cse.yaml or vertex_search.yaml)
        
    Returns:
        CSEClient or VertexSearchClient
    """
    search_engine = os.getenv("SEARCH_ENGINE", "cse").lower()
    
    if search_engine == "vertex":
        logger.info("search_client_factory", engine="vertex_ai_search")
        
        # Vertex AI Search configuration
        project_id = os.getenv("VERTEX_PROJECT_ID", "")
        datastore_id = os.getenv("VERTEX_DATASTORE_ID", "")
        location = os.getenv("VERTEX_LOCATION", "global")
        
        if not project_id or not datastore_id:
            logger.error(
                "vertex_config_missing",
                msg="Set VERTEX_PROJECT_ID and VERTEX_DATASTORE_ID in .env"
            )
            # Fallback to CSE
            logger.warning("vertex_fallback_to_cse", msg="Falling back to Google CSE")
            return create_cse_client(config)
        
        return VertexSearchClient(
            project_id=project_id,
            location=location,
            datastore_id=datastore_id,
            timeout=int(config.get("timeout_seconds", 30)),
        )
    
    else:
        logger.info("search_client_factory", engine="google_cse")
        return create_cse_client(config)


def create_cse_client(config: Dict[str, Any]) -> CSEClient:
    """
    Create Google Custom Search client.
    
    Args:
        config: CSE configuration
        
    Returns:
        CSEClient
    """
    return CSEClient(
        api_key=config["api_key"],
        cx=config["cx"],
        timeout=int(config.get("timeout_seconds", 30)),
    )

