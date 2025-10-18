# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Leopoldo Carvalho Correia de Lima

"""Data Access Objects for judge cache operations."""

import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import JudgeCache


class JudgeCacheDAO:
    """DAO for JudgeCache operations."""
    
    @staticmethod
    def _hash_url(url: str) -> str:
        """Compute SHA256 hash of URL."""
        return hashlib.sha256(url.encode()).hexdigest()
    
    @staticmethod
    def get(session: Session, url: str, plan_goal_hash: str) -> Optional[JudgeCache]:
        """
        Get cached judge decision for URL.
        
        Args:
            session: DB session
            url: URL to check
            plan_goal_hash: Hash of plan goal (for cache invalidation)
            
        Returns:
            JudgeCache if found and valid, None otherwise
        """
        url_hash = JudgeCacheDAO._hash_url(url)
        
        stmt = select(JudgeCache).where(
            JudgeCache.url_hash == url_hash,
            JudgeCache.plan_goal_hash == plan_goal_hash,
            JudgeCache.expires_at > datetime.utcnow()
        )
        
        return session.scalar(stmt)
    
    @staticmethod
    def set(
        session: Session,
        url: str,
        decision: str,
        plan_goal_hash: str,
        ttl_days: int,
        reason: Optional[str] = None,
        violations: Optional[List[str]] = None,
    ) -> JudgeCache:
        """
        Save judge decision to cache.
        
        Args:
            session: DB session
            url: URL
            decision: 'approved' or 'rejected'
            plan_goal_hash: Hash of plan goal
            ttl_days: Time to live in days
            reason: Rejection reason (if rejected)
            violations: List of violations (if rejected)
            
        Returns:
            JudgeCache record
        """
        url_hash = JudgeCacheDAO._hash_url(url)
        
        # Check if exists
        existing = session.query(JudgeCache).filter_by(url_hash=url_hash).first()
        
        if existing:
            # Update existing
            existing.url = url
            existing.decision = decision
            existing.reason = reason
            existing.violations = json.dumps(violations) if violations else None
            existing.plan_goal_hash = plan_goal_hash
            existing.created_at = datetime.utcnow()
            existing.expires_at = datetime.utcnow() + timedelta(days=ttl_days)
            cache = existing
        else:
            # Create new
            cache = JudgeCache(
                url_hash=url_hash,
                url=url,
                decision=decision,
                reason=reason,
                violations=json.dumps(violations) if violations else None,
                plan_goal_hash=plan_goal_hash,
                expires_at=datetime.utcnow() + timedelta(days=ttl_days),
            )
            session.add(cache)
        
        session.flush()
        return cache
    
    @staticmethod
    def get_batch(
        session: Session,
        urls: List[str],
        plan_goal_hash: str,
    ) -> dict:
        """
        Get cached decisions for multiple URLs.
        
        Args:
            session: DB session
            urls: List of URLs to check
            plan_goal_hash: Hash of plan goal
            
        Returns:
            Dict mapping url -> JudgeCache
        """
        # Hash all URLs
        url_hashes = [JudgeCacheDAO._hash_url(url) for url in urls]
        
        stmt = select(JudgeCache).where(
            JudgeCache.url_hash.in_(url_hashes),
            JudgeCache.plan_goal_hash == plan_goal_hash,
            JudgeCache.expires_at > datetime.utcnow()
        )
        
        results = list(session.scalars(stmt))
        
        return {cache.url: cache for cache in results}
    
    @staticmethod
    def cleanup_expired(session: Session) -> int:
        """
        Remove expired cache entries.
        
        Args:
            session: DB session
            
        Returns:
            Number of entries deleted
        """
        stmt = select(JudgeCache).where(
            JudgeCache.expires_at <= datetime.utcnow()
        )
        
        expired = list(session.scalars(stmt))
        count = len(expired)
        
        for cache in expired:
            session.delete(cache)
        
        session.flush()
        return count

