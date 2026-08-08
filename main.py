"""
PROJECT AEGIS — MASTER EXECUTION HARNESS (CHUNKS 1 & 2)
Full End-to-End Pipeline: Ingress -> RedisVL Cache -> Parallel Retrieval -> NLI Gate -> OTel Tracing
"""

import asyncio
import time
import logging

from src.security import IngressSecurityService
from src.cache import RedisVLSemanticCache
from src.mcp import AegisMCPToolRegistry
from src.telemetry import OTelSpanTracer
from src.orchestration import build_aegis_state_machine, AegisExecutionState

# Before (__init__.py empty):
from src.gateway.aegis_federation_gateway import AegisFederationGateway
from src.gateway.sidecar_ingress import IngressContext
from src.security.malicious_content_filter import PromptInjectionFilter

# After (using clean __init__.py exports):
#from gateway import AegisFederationGateway, IngressContext
#from security import PromptInjectionFilter


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AegisMainHarness")


async def run_aegis_pipeline():
    print("\n================ STARTING AEGIS FULL PIPELINE (CHUNKS 1 & 2) ================\n")

    # 1. INGRESS & ZERO-TRUST JWT CHECK
    raw_jwt = {
        "jti": "jwt_token_88491",
        "tenant_id": "AEGIS_HOLDINGS_COMMERCIAL",
        "sub": "LOAN_OFFICER_481",
        "roles": ["COMMERCIAL_LOAN_OFFICER"],
        "abac": {"tier": "SENIOR", "max_approval_limit": 10000000}
    }
    jwt_ctx = IngressSecurityService.extract_security_context(raw_jwt)
    logger.info(f"[Ingress] Authenticated Tenant={jwt_ctx.tenant_id}, User={jwt_ctx.user_id}")

    # 2. PII SCRUBBING
    user_query = "Can Subsidiary B issue $5,000,000 in new debt for ACCT: 994812301 under Parent Corp 2024 amendment?"
    sanitized = IngressSecurityService.sanitize_input(user_query)
    logger.info(f"[Sanitizer] Sanitized Query: {sanitized.sanitized_query}")

    # 3. REDISVL CACHE LOOKUP
    cache = RedisVLSemanticCache(similarity_threshold=0.94)
    cached_res = cache.get(sanitized.sanitized_query, jwt_ctx.tenant_id)

    if cached_res:
        logger.info(f"[Cache HIT] Returning sub-15ms cached answer: {cached_res}")
        return

    logger.info("[Cache MISS] Executing Full Aegis LangGraph Agentic Pipeline...")

    # 4. INITIALIZE OTEL TRACER
    tracer = OTelSpanTracer(trace_id="trace_aegis_99182", tenant_id=jwt_ctx.tenant_id)

    # 5. INITIALIZE LANGGRAPH STATE
    state_input = AegisExecutionState({
        "tenant_id": jwt_ctx.tenant_id,
        "abac_roles": jwt_ctx.roles,
        "query": sanitized.sanitized_query,
        "target_entity": "Subsidiary B",
        "tracer": tracer,
        "vector_docs": [],
        "graph_nodes": [],
        "generated_answer": "",
        "nli_score": 0.0,
        "nli_gate_passed": False,
        "final_output": ""
    })

    # 6. EXECUTE LANGGRAPH WORKFLOW
    app = build_aegis_state_machine()
    start_time = time.time()
    
    result = await app.ainvoke(state_input)
    
    total_time = (time.time() - start_time) * 1000

    # 7. POPULATE REDISVL CACHE FOR SUBSEQUENT RUNS
    cache.set(sanitized.sanitized_query, jwt_ctx.tenant_id, {"answer": result["final_output"]}, compute_time_ms=total_time)

    # 8. DISPLAY BENCHMARK SUMMARY
    print("\n================ PIPELINE BENCHMARK SUMMARY ================")
    print(f"Total Pipeline Latency:  {total_time:.2f} ms (Target: <3000 ms)")
    print(f"NLI Faithfulness Score:  {result['nli_score']} (Threshold: >=0.90, Passed: {result['nli_gate_passed']})")
    print(f"Registered MCP Tools:    {AegisMCPToolRegistry.get_opensearch_mcp_schema()['name']}, {AegisMCPToolRegistry.get_neptune_mcp_schema()['name']}")
    print(f"\nFinal Verified Output:\n{result['final_output']}")
    print("============================================================\n")

async def main():
    gateway = AegisFederationGateway()
    
    test_context = IngressContext(
        user_id="dr_house_99",
        tenant_id="kaiser_clinics_west",
        roles=["clinician"],
        raw_prompt="Can you check patient John Doe MRN-55412 clinical longitudinal record and formulary status?"
    )

    print("--- INITIATING AEGIS INGRESS PIPELINE ---")
    result = await gateway.handle_request(test_context)
    print("\n[GATEWAY RESULT OUTPUT]:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

#if __name__ == "__main__":
#    asyncio.run(run_aegis_pipeline())