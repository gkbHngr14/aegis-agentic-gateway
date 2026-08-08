"""
Unified Grand Slam Chaos Runner: Executes Vectors 1, 2, 3, and 4 against Aegis.
"""

import sys
import time
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.gateway import AegisFederationGateway, IngressContext
from src.gateway.nli_guardrail import NLIGuardrailEngine
from src.security.token_vault import TenantIsolatedTokenVault
from tests.chaos.payload_mutator import PayloadMutator
from tests.chaos.vault_mutator import VaultMutator
from tests.chaos.mcp_mutator import MCPMutator
from tests.chaos.nli_mutator import NLIMutator


class AgenticChaosTester:

    def __init__(self):
        self.gateway = AegisFederationGateway()
        self.nli_engine = NLIGuardrailEngine(entailment_threshold=0.90, max_latency_ms=25.0)
        self.vault = TenantIsolatedTokenVault(ttl_seconds=30.0)

    async def run_vector_1_security_fuzzing(self) -> bool:
        print("\n" + "=" * 65)
        print("🔥 [VECTOR 1] INITIATING SECURITY FUZZING RUN 🔥")
        print("=" * 65)

        attack_matrix = PayloadMutator.generate_attack_matrix()
        total_attacks = len(attack_matrix)
        blocked_count = 0

        for idx, attack in enumerate(attack_matrix, 1):
            ctx = IngressContext(
                user_id=f"chaos_agent_{idx}",
                tenant_id="kaiser_clinics_west",
                roles=["clinician"],
                raw_prompt=attack["prompt"],
            )

            start_t = time.perf_counter()
            response = await self.gateway.handle_request(ctx)
            elapsed_ms = (time.perf_counter() - start_t) * 1000

            is_blocked = response.get("status") == "SECURITY_REJECTED"
            if is_blocked:
                blocked_count += 1

            status_icon = "🟢 BLOCKED" if is_blocked else "🔴 LEAKED"
            print(f"[{idx:02d}/{total_attacks:02d}] {attack['type']:<24} | {status_icon} | {elapsed_ms:.3f}ms")

        return blocked_count == total_attacks

    async def run_vector_2_vault_privacy_chaos(self) -> bool:
        print("\n" + "=" * 65)
        print("🔒 [VECTOR 2] INITIATING TOKEN VAULT & PRIVACY LEAKAGE CHAOS RUN 🔒")
        print("=" * 65)

        probes = VaultMutator.generate_privacy_probes()
        passed_probes = 0
        total_probes = len(probes)

        for idx, probe in enumerate(probes, 1):
            # 1. Ingress: Owner tenant masks & stores
            masked_text, _ = self.vault.mask_and_store(
                tenant_id=probe["owner_tenant"],
                trace_id=probe["trace_id"],
                raw_text=probe["raw_text"],
            )

            # 2. Egress: Caller tenant attempts async re-hydration
            start_t = time.perf_counter()
            forced_now = time.time() + probe["ttl_offset_sec"]
            
            rehydrated_text, success, reason = await self.vault.rehydrate_async(
                tenant_id=probe["caller_tenant"],
                trace_id=probe["trace_id"],
                masked_text=masked_text,
                user_roles=probe["caller_roles"],
                forced_time=forced_now,
            )
            elapsed_ms = (time.perf_counter() - start_t) * 1000

            matches_expectation = success == probe["expected_success"]
            if matches_expectation:
                passed_probes += 1

            status_icon = "🟢 DEFENDED" if matches_expectation else "🔴 PRIVACY BREACH"
            res_str = "REHYDRATED" if success else f"BLOCKED ({reason})"

            print(
                f"[{idx:02d}/{total_probes:02d}] Probe: {probe['type']:<26} | "
                f"{status_icon} | {res_str} | {elapsed_ms:.3f}ms"
            )

        print("\n" + "=" * 65)
        print(f"📊 VECTOR 2 SUMMARY: {passed_probes}/{total_probes} Probes Passed")
        print("=" * 65 + "\n")

        return passed_probes == total_probes

    async def run_vector_3_mcp_protocol_chaos(self) -> bool:
        print("\n" + "=" * 65)
        print("⚡️ [VECTOR 3] INITIATING MCP PROTOCOL & SCHEMA CHAOS RUN ⚡️")
        print("=" * 65)

        mcp_registry = self.gateway.tool_registry
        passed_tests = 0
        corrupted_payloads = MCPMutator.generate_corrupted_schemas()
        total_mcp_tests = len(corrupted_payloads) + 2

        for idx, item in enumerate(corrupted_payloads, 1):
            rejected = not mcp_registry.register_tool(f"corrupted_tool_{idx}", item["schema"])
            if rejected:
                passed_tests += 1
            print(f"[{idx:02d}/{total_mcp_tests:02d}] Schema Test: {item['type']:<25} | {'🟢 DEFENDED' if rejected else '🔴 ACCEPTED'}")

        flood = MCPMutator.generate_context_flood(500)
        for t_id, schema in flood.items():
            mcp_registry.register_tool(t_id, schema)

        retrieved = await mcp_registry.retrieve_relevant_tools("Check FHIR history")
        pruned = len(retrieved) <= mcp_registry.max_context_tools
        if pruned:
            passed_tests += 1
        print(f"[{total_mcp_tests-1:02d}/{total_mcp_tests:02d}] Context Flood Test (500 tools)  | "
              f"{'🟢 DEFENDED (PRUNED)' if pruned else '🔴 BLOATED'} ({len(retrieved)} active)")

        start_t = time.perf_counter()
        mcp_registry.lookup_timeout_ms = 10.0

        async def hanging_retrieval(prompt: str):
            await MCPMutator.simulate_hanging_tool_call(0.5)
            return {}

        mcp_registry._execute_retrieval = hanging_retrieval
        fallback_res = await mcp_registry.retrieve_relevant_tools("Check patient")
        elapsed_ms = (time.perf_counter() - start_t) * 1000

        timed_out = elapsed_ms < 100.0 and len(fallback_res) > 0
        if timed_out:
            passed_tests += 1
        print(f"[{total_mcp_tests:02d}/{total_mcp_tests:02d}] Latency Hang Test (500ms delay) | "
              f"{'🟢 DEFENDED (FALLBACK)' if timed_out else '🔴 HUNG'} ({elapsed_ms:.2f}ms)")

        return passed_tests == total_mcp_tests

    async def run_vector_4_nli_boundary_chaos(self) -> bool:
        print("\n" + "=" * 65)
        print("🧠 [VECTOR 4] INITIATING NLI GUARDRAIL & LATENCY BUDGET CHAOS RUN 🧠")
        print("=" * 65)

        probes = NLIMutator.generate_nli_probes()
        passed_probes = 0
        total_probes = len(probes)

        for idx, probe in enumerate(probes, 1):
            start_t = time.perf_counter()
            passed, score, method = await self.nli_engine.evaluate_faithfulness(
                context=probe["context"],
                candidate=probe["candidate"],
                forced_delay_ms=probe["simulate_delay_ms"],
            )
            elapsed_ms = (time.perf_counter() - start_t) * 1000

            matches_expectation = passed == probe["expected_pass"]
            if matches_expectation:
                passed_probes += 1

            status_icon = "🟢 VERIFIED" if matches_expectation else "🔴 UNEXPECTED"
            print(f"[{idx:02d}/{total_probes:02d}] Probe: {probe['type']:<24} | "
                  f"{status_icon} | Score: {score:.2f} [{method}] | {elapsed_ms:.2f}ms")

        return passed_probes == total_probes


async def main():
    tester = AgenticChaosTester()
    v1 = await tester.run_vector_1_security_fuzzing()
    v2 = await tester.run_vector_2_vault_privacy_chaos()
    v3 = await tester.run_vector_3_mcp_protocol_chaos()
    v4 = await tester.run_vector_4_nli_boundary_chaos()

    if v1 and v2 and v3 and v4:
        print("\n" + "🏆" * 32)
        print("   GRAND SLAM WALL OF FAME! AEGIS CLEARED ALL 4 VECTORS!  ")
        print("🏆" * 32 + "\n")
    else:
        print("\n💀 [VERDICT] WALL OF SHAME! Build Rejected!\n")


if __name__ == "__main__":
    asyncio.run(main())