"""
PROJECT AEGIS — CHUNK 1: INGRESS, ABAC, REDISVL CACHE & MCP SCHEMAS
Architecture Benchmark: Sub-15ms Cache Lookup, Strict Tenant Isolation, MCP Standard
"""

import math
import time
import random
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AegisIngressEngine")


# ---------------------------------------------------------------------------
# 1. SECURITY & INGRESS CONTEXT SCHEMAS
# ---------------------------------------------------------------------------

@dataclass
class OAuthJWTContext:
    token_id: str
    tenant_id: str
    user_id: str
    roles: List[str]
    abac_attributes: Dict[str, Any]


@dataclass
class SanitizedPayload:
    raw_query: str
    sanitized_query: str
    pii_detected: bool
    redacted_fields: List[str]

# ---------------------------------------------------------------------------
# 2. INGRESS & PII SCRUBBING SERVICE
# ---------------------------------------------------------------------------
class UnauthorizedException(Exception):
    """Raised when mandatory JWT security claims are missing."""
    pass

class IngressSecurityService:
    @staticmethod
    def extract_security_context(raw_jwt: Dict[str, Any]) -> OAuthJWTContext:
        """Parses JWT token claims and enforces strict tenant/ABAC boundary requirements."""
        
        # Enforce mandatory security claims
        if "tenant_id" not in raw_jwt:
            raise UnauthorizedException("SECURITY VIOLATION: Missing mandatory 'tenant_id' claim in JWT.")
        if "jti" not in raw_jwt:
            raise UnauthorizedException("SECURITY VIOLATION: Missing mandatory 'jti' (token_id) claim in JWT.")
            
        return OAuthJWTContext(
            token_id=raw_jwt["jti"],            # Direct key access raises KeyError if missing
            tenant_id=raw_jwt["tenant_id"],      # Hard requirement
            user_id=raw_jwt.get("sub", "anonymous_user"),
            roles=raw_jwt.get("roles", []),
            abac_attributes=raw_jwt.get("abac", {})
        )
        
    @staticmethod
    def sanitize_input(query_text: str) -> SanitizedPayload:
        """Simulates Presidio PII scrubbing (SSNs, Account Numbers, Tax IDs)."""
        redacted_fields = []
        sanitized = query_text

        # SSN Redaction
        if "SSN:" in sanitized or "ssn" in sanitized.lower():
            sanitized = " ".join([w if not w.replace("-", "").isdigit() or len(w) < 9 else "[REDACTED_SSN]" for w in sanitized.split()])
            redacted_fields.append("SSN")

        # Account Number Redaction (Simulated pattern)
        if "ACCT:" in sanitized:
            sanitized = sanitized.replace("ACCT:", "ACCT: [REDACTED_ACCT]")
            redacted_fields.append("ACCOUNT_NUMBER")

        return SanitizedPayload(
            raw_query=query_text,
            sanitized_query=sanitized,
            pii_detected=len(redacted_fields) > 0,
            redacted_fields=redacted_fields
        )