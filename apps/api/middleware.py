# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Middleware for request tracking and logging."""

import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with trace ID."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging."""
        # Generate trace ID
        trace_id = str(uuid.uuid4())
        
        # Bind trace_id to logger context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
        
        # Log request
        start_time = time.time()
        
        logger.info(
            "request_start",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        
        logger.info(
            "request_complete",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        
        # Add trace ID to response headers
        response.headers["X-Trace-ID"] = trace_id
        
        return response

