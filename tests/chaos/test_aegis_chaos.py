"""
PyTest Test Suite: Agentic Chaos Release Gate (Vectors 1 - 4).
Runs deterministically in CI/CD pipeline to gate production releases.
"""

import pytest
import pytest_asyncio
from tests.chaos.chaos_runner import AgenticChaosTester


@pytest_asyncio.fixture(scope="module")
async def chaos_tester():
    """Module-level fixture initializing the Aegis Chaos Engine instance."""
    return AgenticChaosTester()


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.security
async def test_vector_1_security_injections(chaos_tester):
    """Vector 1: Verifies 100% block rate against polymorphic injection vectors."""
    passed = await chaos_tester.run_vector_1_security_fuzzing()
    assert passed, (
        "💀 [CI GATE REJECTED] Vector 1 breached! Security sidecar leaked obfuscated injections."
    )


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.privacy
async def test_vector_2_tenant_privacy_vault(chaos_tester):
    """Vector 2: Verifies tenant isolation, ABAC enforcement, and TTL cache auto-purge."""
    passed = await chaos_tester.run_vector_2_vault_privacy_chaos()
    assert passed, (
        "💀 [CI GATE REJECTED] Vector 2 breached! Token Vault cross-tenant leak or ABAC bypass detected."
    )


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.mcp
async def test_vector_3_mcp_protocol_chaos(chaos_tester):
    """Vector 3: Verifies resilience against schema mutations, context floods, and hangs."""
    passed = await chaos_tester.run_vector_3_mcp_protocol_chaos()
    assert passed, (
        "💀 [CI GATE REJECTED] Vector 3 breached! Unhandled MCP schema corruption or latency hang."
    )


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.guardrails
async def test_vector_4_nli_guardrail_sla(chaos_tester):
    """Vector 4: Verifies numerical claim validation and sub-25ms SLA timeout fallbacks."""
    passed = await chaos_tester.run_vector_4_nli_boundary_chaos()
    assert passed, (
        "💀 [CI GATE REJECTED] Vector 4 breached! NLI hallucination leaked or SLA timeout failed."
    )