from typing import List, Dict, Any, Optional
from .sidecar_ingress import IngressContext, SecurityGatewaySidecar
from .mcp_registry import DynamicToolRegistry
from .nli_guardrail import LocalGuardrailEngine

class AegisFederationGateway:
    def __init__(self):
        self.security = SecurityGatewaySidecar()
        self.tool_registry = DynamicToolRegistry()
        self.guardrails = LocalGuardrailEngine()

    async def handle_request(self, ctx: IngressContext) -> Dict[str, Any]:
        # Step 1: Synchronous Ingress Security & ABAC (via Java 21 / Asyncio Virtual Threads model)
        secured_ctx = await self.security.process_ingress(ctx)
        
        # SHORT-CIRCUIT: Rejects malicious prompts before LLM or Vector store invocation
        if secured_ctx.security_violation:
            return {
                "status": "SECURITY_REJECTED",
                "reason": secured_ctx.security_violation,
                "action": "SHORT_CIRCUITED_BEFORE_LLM",
            }

        # Step 2: Dynamic Tool Retrieval (Pruning token bloat)
        active_tools = await self.tool_registry.retrieve_relevant_tools(secured_ctx.sanitized_prompt)

        # Step 3: Model Execution (Simulated LLM response generation using scoped tokens)
        llm_response = f"Processed request for tenant {secured_ctx.tenant_id} using tools: {list(active_tools.keys())}."

        # Step 4: Egress NLI Guardrail Check
        entailment_score = await self.guardrails.evaluate_faithfulness(secured_ctx.sanitized_prompt, llm_response)

        if entailment_score < 0.90:
            return {
                "status": "FALLBACK_TRIGGERED",
                "reason": "Faithfulness score below 0.90 threshold",
                "fallback_payload": "Deterministic citation-backed default response."
            }

        return {
            "status": "SUCCESS",
            "sanitized_input": secured_ctx.sanitized_prompt,
            "tools_injected": list(active_tools.keys()),
            "response": llm_response,
            "nli_score": entailment_score
        }