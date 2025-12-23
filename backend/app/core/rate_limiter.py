"""
=============================================================================
RATE LIMITER
=============================================================================

Rate limiting implementation for API endpoints.

Features:
- In-memory rate limiting (production: Redis)
- Per-IP and per-user limits
- Configurable windows and limits
- Brute-force protection for login

AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

import time
import logging
from typing import Dict, Tuple, Optional
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status

from app.config import settings

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# RATE LIMITER CLASS
# =============================================================================

class RateLimiter:
    """
    In-memory rate limiter.
    
    For production, use Redis-based rate limiting.
    """
    
    def __init__(self):
        """Initialize rate limiter."""
        # Storage: {key: [(timestamp, count), ...]}
        self._storage: Dict[str, list] = defaultdict(list)
        
        # Failed login attempts: {identifier: [(timestamp, ip), ...]}
        self._failed_logins: Dict[str, list] = defaultdict(list)
        
        # Locked accounts: {identifier: unlock_time}
        self._locked_accounts: Dict[str, datetime] = {}
        
        logger.info("RateLimiter initialized (in-memory mode)")
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old entries
        if identifier in self._storage:
            self._storage[identifier] = [
                (ts, count) for ts, count in self._storage[identifier]
                if ts > window_start
            ]
        
        # Count requests in current window
        current_count = sum(
            count for ts, count in self._storage[identifier]
        )
        
        if current_count >= max_requests:
            # Calculate retry after
            oldest_ts = min(ts for ts, _ in self._storage[identifier])
            retry_after = int(window_seconds - (now - oldest_ts)) + 1
            
            logger.warning(
                f"Rate limit exceeded for {identifier[:20]}... "
                f"({current_count}/{max_requests} in {window_seconds}s)"
            )
            
            return False, retry_after
        
        # Add current request
        self._storage[identifier].append((now, 1))
        
        return True, None
    
    def record_failed_login(
        self,
        identifier: str,
        ip_address: str,
        max_attempts: int = 5,
        lockout_minutes: int = 15
    ) -> Tuple[bool, Optional[int], int]:
        """
        Record a failed login attempt.
        
        Args:
            identifier: Email or username
            ip_address: IP address
            max_attempts: Maximum failed attempts before lockout
            lockout_minutes: Lockout duration in minutes
            
        Returns:
            Tuple of (is_locked, unlock_after_seconds, remaining_attempts)
        """
        now = datetime.now(timezone.utc)
        
        # Check if already locked
        if identifier in self._locked_accounts:
            unlock_time = self._locked_accounts[identifier]
            if now < unlock_time:
                seconds_left = int((unlock_time - now).total_seconds())
                logger.warning(f"Account locked: {identifier[:20]}... ({seconds_left}s remaining)")
                return True, seconds_left, 0
            else:
                # Unlock account
                del self._locked_accounts[identifier]
                self._failed_logins[identifier] = []
        
        # Record failed attempt
        self._failed_logins[identifier].append((now, ip_address))
        
        # Clean old attempts (older than lockout window)
        window_start = now - timedelta(minutes=lockout_minutes)
        self._failed_logins[identifier] = [
            (ts, ip) for ts, ip in self._failed_logins[identifier]
            if ts > window_start
        ]
        
        # Count recent attempts
        recent_attempts = len(self._failed_logins[identifier])
        remaining = max(0, max_attempts - recent_attempts)
        
        # Check if should lock
        if recent_attempts >= max_attempts:
            unlock_time = now + timedelta(minutes=lockout_minutes)
            self._locked_accounts[identifier] = unlock_time
            seconds_left = lockout_minutes * 60
            
            logger.critical(
                f"Account locked due to {recent_attempts} failed attempts: "
                f"{identifier[:20]}... from IPs: {[ip for _, ip in self._failed_logins[identifier]]}"
            )
            
            return True, seconds_left, 0
        
        logger.info(f"Failed login recorded: {identifier[:20]}... ({remaining} attempts remaining)")
        
        return False, None, remaining
    
    def clear_failed_logins(self, identifier: str):
        """Clear failed login attempts after successful login."""
        if identifier in self._failed_logins:
            del self._failed_logins[identifier]
        if identifier in self._locked_accounts:
            del self._locked_accounts[identifier]
        logger.info(f"Failed login attempts cleared: {identifier[:20]}...")
    
    def is_account_locked(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if account is currently locked.
        
        Returns:
            Tuple of (is_locked, unlock_after_seconds)
        """
        if identifier not in self._locked_accounts:
            return False, None
        
        now = datetime.now(timezone.utc)
        unlock_time = self._locked_accounts[identifier]
        
        if now >= unlock_time:
            # Unlock
            del self._locked_accounts[identifier]
            return False, None
        
        seconds_left = int((unlock_time - now).total_seconds())
        return True, seconds_left


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

rate_limiter = RateLimiter()


# =============================================================================
# FASTAPI DEPENDENCIES
# =============================================================================

def check_rate_limit_dependency(
    max_requests: int = 60,
    window_seconds: int = 60
):
    """
    FastAPI dependency for rate limiting.
    
    Usage:
        @router.get("/endpoint", dependencies=[Depends(check_rate_limit_dependency(max_requests=10, window_seconds=60))])
    """
    async def dependency(request: Request):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        is_allowed, retry_after = rate_limiter.check_rate_limit(
            identifier=client_ip,
            max_requests=max_requests,
            window_seconds=window_seconds
        )
        
        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)}
            )
    
    return dependency


def check_login_rate_limit(request: Request):
    """
    Specific rate limiter for login endpoint.
    
    Stricter limits to prevent brute-force attacks.
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # 5 login attempts per minute per IP
    is_allowed, retry_after = rate_limiter.check_rate_limit(
        identifier=f"login:{client_ip}",
        max_requests=5,
        window_seconds=60
    )
    
    if not is_allowed:
        logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)}
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def record_failed_login(email: str, ip_address: str) -> Tuple[bool, Optional[int], int]:
    """
    Record a failed login attempt.
    
    Returns:
        Tuple of (is_locked, unlock_after_seconds, remaining_attempts)
    """
    return rate_limiter.record_failed_login(
        identifier=email.lower(),
        ip_address=ip_address,
        max_attempts=5,  # 5 failed attempts
        lockout_minutes=15  # 15 minute lockout
    )


def clear_failed_logins(email: str):
    """Clear failed login attempts after successful login."""
    rate_limiter.clear_failed_logins(email.lower())


def is_account_locked(email: str) -> Tuple[bool, Optional[int]]:
    """Check if account is locked due to failed login attempts."""
    return rate_limiter.is_account_locked(email.lower())









