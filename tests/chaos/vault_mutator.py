"""
Vault Mutator: Generates cross-tenant token leakage attempts, unauthorized
ABAC re-hydration calls, and expired TTL probe vectors.
"""

from typing import List, Dict, Any


class VaultMutator:

    @staticmethod
    def generate_privacy_probes() -> List[Dict[str, Any]]:
        return [
            # 1. Authorized In-Tenant Re-hydration (Should Succeed)
            {
                "type": "AUTHORIZED_REHYDRATION",
                "owner_tenant": "kaiser_clinics_west",
                "caller_tenant": "kaiser_clinics_west",
                "trace_id": "req_trace_001",
                "caller_roles": ["clinician"],
                "raw_text": "Patient John Doe presented with severe fever.",
                "ttl_offset_sec": 0.0,
                "expected_success": True,
            },
            # 2. Cross-Tenant Token Theft Attempt (Tenant B accessing Tenant A token -> Should Block)
            {
                "type": "CROSS_TENANT_LEAK_ATTEMPT",
                "owner_tenant": "kaiser_clinics_west",
                "caller_tenant": "sutter_health_east",  # ATTACKER TENANT
                "trace_id": "req_trace_001",
                "caller_roles": ["clinician"],
                "raw_text": "Patient John Doe presented with severe fever.",
                "ttl_offset_sec": 0.0,
                "expected_success": False,
            },
            # 3. Unauthorized ABAC Role Re-hydration (Billing clerk role -> Should Block)
            {
                "type": "UNAUTHORIZED_ABAC_ROLE",
                "owner_tenant": "kaiser_clinics_west",
                "caller_tenant": "kaiser_clinics_west",
                "trace_id": "req_trace_002",
                "caller_roles": ["billing_clerk"],  # Lacks 'clinician' role
                "raw_text": "Patient Jane Smith requested records.",
                "ttl_offset_sec": 0.0,
                "expected_success": False,
            },
            # 4. Expired TTL Vault Mining (Requesting token after 35s > 30s TTL -> Should Block)
            {
                "type": "EXPIRED_TTL_MINING",
                "owner_tenant": "kaiser_clinics_west",
                "caller_tenant": "kaiser_clinics_west",
                "trace_id": "req_trace_003",
                "caller_roles": ["clinician"],
                "raw_text": "Patient John Doe presented with severe fever.",
                "ttl_offset_sec": 35.0,  # Expired
                "expected_success": False,
            },
        ]