"""
=============================================================================
SECURITY MODULE
=============================================================================

PURPOSE:
    Handles all security-related operations:
    - JWT token creation and verification
    - Password hashing and verification
    - Token blacklisting for logout

=============================================================================
JWT TOKENS EXPLAINED
=============================================================================

WHAT IS JWT?
    JSON Web Token - a compact, URL-safe way to transmit claims.
    Structure: header.payload.signature
    
    Example decoded:
    {
        "sub": "user-uuid-here",       # Subject (user ID)
        "exp": 1701234567,              # Expiration timestamp
        "type": "access",               # Token type
        "iat": 1701234267               # Issued at
    }

TWO TOKEN TYPES:
    1. Access Token:
       - Short-lived (30 minutes)
       - Sent with every API request
       - Contains user ID
       
    2. Refresh Token:
       - Long-lived (7 days)
       - Used only to get new access tokens
       - Stored securely by client

WHY TWO TOKENS?
    - If access token is stolen, it expires quickly
    - Refresh tokens can be revoked (logout)
    - Better security without constant re-login

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Dict, Union
from uuid import UUID

# JWT handling
from jose import jwt, JWTError, ExpiredSignatureError

# Password hashing
from passlib.context import CryptContext

# Redis for token blacklist (optional, can use in-memory for dev)
# from redis import Redis

# Local imports
from app.config import settings

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# PASSWORD HASHING
# =============================================================================

# Password context with bcrypt
# WHY bcrypt?
#   - Industry standard
#   - Resistant to GPU attacks
#   - Automatic salt generation
#   - Configurable work factor
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # 2^12 iterations
)


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password.
    
    Uses bcrypt with automatic salt generation.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
        
    Example:
        hash = get_password_hash("SecurePass123!")
        # Returns: "$2b$12$..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        plain_password: Password to verify
        hashed_password: Stored hash
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================================================
# TOKEN TYPES
# =============================================================================

class TokenType(str, Enum):
    """Token types for JWT."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    EMAIL_VERIFICATION = "email_verification"


# =============================================================================
# TOKEN BLACKLIST (In-Memory for Development)
# =============================================================================

# In production, use Redis or database for token blacklist
# This allows proper logout by invalidating tokens

_token_blacklist: set = set()


def blacklist_token(token: str) -> None:
    """
    Add token to blacklist (for logout).
    
    In production, use Redis with expiration matching token expiry.
    
    Args:
        token: JWT token to blacklist
    """
    _token_blacklist.add(token)
    logger.info(f"Token blacklisted. Blacklist size: {len(_token_blacklist)}")


def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted.
    
    Args:
        token: JWT token to check
        
    Returns:
        True if blacklisted, False otherwise
    """
    return token in _token_blacklist


def clear_expired_from_blacklist() -> None:
    """
    Clean up expired tokens from blacklist.
    
    Should be run periodically (e.g., by a background task).
    In production, Redis TTL handles this automatically.
    """
    # In-memory implementation doesn't track expiry
    # For production, implement with Redis or database
    pass


# =============================================================================
# JWT TOKEN CREATION
# =============================================================================

def create_access_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a new access token.
    
    Access tokens are short-lived and used for API authentication.
    
    Args:
        subject: User ID (typically UUID as string)
        expires_delta: Custom expiration time
        additional_claims: Extra data to include in token
        
    Returns:
        Encoded JWT token string
        
    Example:
        token = create_access_token(
            subject=str(user.id),
            additional_claims={"role": "admin"}
        )
    """
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Build payload
    to_encode = {
        "sub": str(subject),           # Subject (user ID)
        "exp": expire,                  # Expiration
        "iat": datetime.now(timezone.utc),  # Issued at
        "type": TokenType.ACCESS.value,     # Token type
    }
    
    # Add any additional claims
    if additional_claims:
        to_encode.update(additional_claims)
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    logger.debug(f"Created access token for subject: {subject}")
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, UUID],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new refresh token.
    
    Refresh tokens are long-lived and used only to get new access tokens.
    
    Args:
        subject: User ID
        expires_delta: Custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": TokenType.REFRESH.value,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    logger.debug(f"Created refresh token for subject: {subject}")
    return encoded_jwt


def create_reset_password_token(email: str) -> str:
    """
    Create a password reset token.
    
    Short-lived (1 hour) and contains email for verification.
    
    Args:
        email: User's email address
        
    Returns:
        Encoded JWT token
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": TokenType.RESET_PASSWORD.value,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    logger.info(f"Created password reset token for: {email[:3]}***")
    return encoded_jwt


def create_email_verification_token(email: str) -> str:
    """
    Create an email verification token.
    
    Valid for 24 hours.
    
    Args:
        email: Email to verify
        
    Returns:
        Encoded JWT token
    """
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    
    to_encode = {
        "sub": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": TokenType.EMAIL_VERIFICATION.value,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    logger.info(f"Created email verification token for: {email[:3]}***")
    return encoded_jwt


# =============================================================================
# JWT TOKEN VERIFICATION
# =============================================================================

class TokenPayload:
    """
    Decoded token payload.
    
    Provides structured access to token claims.
    """
    
    def __init__(
        self,
        sub: str,
        exp: datetime,
        iat: datetime,
        token_type: TokenType,
        **additional_claims
    ):
        self.sub = sub                  # Subject (user ID or email)
        self.exp = exp                  # Expiration
        self.iat = iat                  # Issued at
        self.token_type = token_type    # Token type
        self.additional_claims = additional_claims
    
    @property
    def user_id(self) -> str:
        """Get user ID from subject."""
        return self.sub
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.exp


class TokenError(Exception):
    """Base exception for token errors."""
    pass


class TokenExpiredError(TokenError):
    """Token has expired."""
    pass


class TokenInvalidError(TokenError):
    """Token is invalid or malformed."""
    pass


class TokenBlacklistedError(TokenError):
    """Token has been revoked."""
    pass


class TokenTypeMismatchError(TokenError):
    """Wrong token type for operation."""
    pass


def verify_token(
    token: str,
    expected_type: Optional[TokenType] = None,
    check_blacklist: bool = True
) -> TokenPayload:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        expected_type: Expected token type (optional)
        check_blacklist: Whether to check token blacklist
        
    Returns:
        TokenPayload with decoded claims
        
    Raises:
        TokenExpiredError: If token has expired
        TokenInvalidError: If token is malformed
        TokenBlacklistedError: If token was revoked
        TokenTypeMismatchError: If token type doesn't match
        
    Example:
        try:
            payload = verify_token(token, TokenType.ACCESS)
            user_id = payload.user_id
        except TokenExpiredError:
            # Handle expired token
            pass
    """
    # Check blacklist first (fast rejection)
    if check_blacklist and is_token_blacklisted(token):
        logger.warning("Attempted use of blacklisted token")
        raise TokenBlacklistedError("Token has been revoked")
    
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract claims
        sub = payload.get("sub")
        exp = payload.get("exp")
        iat = payload.get("iat")
        token_type = payload.get("type")
        
        if not sub:
            raise TokenInvalidError("Token missing subject")
        
        # Convert timestamps
        exp_dt = datetime.fromtimestamp(exp, tz=timezone.utc) if exp else None
        iat_dt = datetime.fromtimestamp(iat, tz=timezone.utc) if iat else None
        
        # Convert token type
        try:
            token_type_enum = TokenType(token_type) if token_type else TokenType.ACCESS
        except ValueError:
            raise TokenInvalidError(f"Invalid token type: {token_type}")
        
        # Verify token type if specified
        if expected_type and token_type_enum != expected_type:
            raise TokenTypeMismatchError(
                f"Expected {expected_type.value} token, got {token_type_enum.value}"
            )
        
        # Build payload object
        return TokenPayload(
            sub=sub,
            exp=exp_dt,
            iat=iat_dt,
            token_type=token_type_enum,
            **{k: v for k, v in payload.items() 
               if k not in ["sub", "exp", "iat", "type"]}
        )
        
    except ExpiredSignatureError:
        logger.debug("Token verification failed: expired")
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise TokenInvalidError(f"Invalid token: {e}")


def verify_reset_password_token(token: str) -> str:
    """
    Verify password reset token and return email.
    
    Args:
        token: Reset token
        
    Returns:
        Email address from token
        
    Raises:
        TokenError: If token is invalid
    """
    payload = verify_token(
        token,
        expected_type=TokenType.RESET_PASSWORD,
        check_blacklist=False
    )
    return payload.sub


def verify_email_verification_token(token: str) -> str:
    """
    Verify email verification token and return email.
    
    Args:
        token: Verification token
        
    Returns:
        Email address from token
        
    Raises:
        TokenError: If token is invalid
    """
    payload = verify_token(
        token,
        expected_type=TokenType.EMAIL_VERIFICATION,
        check_blacklist=False
    )
    return payload.sub
























