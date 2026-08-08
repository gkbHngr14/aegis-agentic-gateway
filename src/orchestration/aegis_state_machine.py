"""
PROJECT AEGIS — LANGGRAPH ORCHESTRATION ENGINE
Bounded State Machine with Async Retrieval, Local NLI Gate & Non-LLM Fallback
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END

from src.telemetry.otel_tracer import OTelSpanTracer
from src.retrieval.async_retriever import AsyncParallelRetrievalEngine
from src.eval.nli_faithfulness_gate import NLIFaithfulnessGate


logger = logging.getLogger("AegisStateMachine")


class AegisExecutionState(TypedDict, total=False):
    tenant_id: str
    abac_roles: List[str]
    query: str
    target_entity: str
    tracer: Any
    vector_docs: List[Dict[str, Any]]
    graph_nodes: List[Dict[str, Any]]
    generated_answer: str
    nli_score: float
    nli_gate_passed: bool
    final_output: str


# ---------------------------------------------------------------------------
# WORKFLOW NODES
# ---------------------------------------------------------------------------

async def parallel_retrieval_node(state: AegisExecutionState) -> AegisExecutionState:
    """Node 1: Fires OpenSearch Vector RAG and Neptune Cypher Traversal concurrently via asyncio.gather."""
    #tracer: OTelSpanTracer = state["tracer"]
    tracer = state.get("tracer")
    start = time.time()
    
    v_task = AsyncParallelRetrievalEngine.opensearch_search(state["query"], state["tenant_id"], state["abac_roles"])
    g_task = AsyncParallelRetrievalEngine.neptune_traversal(state["target_entity"], state["tenant_id"])
    
    vector_results, graph_results = await asyncio.gather(v_task, g_task)
    
    duration = (time.time() - start) * 1000

    if tracer:
        tracer.record_span("async_parallel_retrieval", duration, {"vector_count": len(vector_results), "graph_count": len(graph_results)})
    #tracer.record_span("async_parallel_retrieval", duration, {"vector_count": len(vector_results), "graph_count": len(graph_results)})
    
    state["vector_docs"] = vector_results
    state["graph_nodes"] = graph_results
    return state


async def llm_generation_node(state: AegisExecutionState) -> AegisExecutionState:
    """Node 2: Bedrock LLM Streaming Generation + TTFT SLA Measurement."""
    tracer = state.get("tracer")
    #tracer: OTelSpanTracer = state["tracer"]
    start = time.time()
    
    # Simulate Bedrock Streaming TTFT (620ms)
    await asyncio.sleep(0.62)
    ttft_ms = (time.time() - start) * 1000

    if tracer:
        tracer.record_span("llm_time_to_first_token", ttft_ms, {"model": "claude-3-5-sonnet", "sla_met": ttft_ms <= 800})
    
    state["generated_answer"] = (
        "NO. Subsidiary B cannot issue $5,000,000 in new debt. "
        "Under Section 2.04 of the March 2024 Amendment, Restricted Subsidiaries are capped at $2,000,000. "
        "Amazon Neptune Knowledge Graph confirms Subsidiary B is classified as a Restricted Subsidiary."
    )
    return state


async def local_nli_faithfulness_node(state: AegisExecutionState) -> AegisExecutionState:
    """Node 3: Local DeBERTa Cross-Encoder Faithfulness Gate (>0.90 Entailment Score)."""
    tracer = state.get("tracer")
    #tracer: OTelSpanTracer = state["tracer"]
    start = time.time()
    
    premise_text = " ".join([d["text"] for d in state["vector_docs"]])
    nli_score = await NLIFaithfulnessGate.evaluate_faithfulness(premise_text, state["generated_answer"])
    
    duration = 30.0  # 30ms simulation
    state["nli_score"] = nli_score
    state["nli_gate_passed"] = nli_score >= 0.90
    
    if tracer:
        tracer.record_span("local_nli_faithfulness_gate", duration, {"score": nli_score, "gate_passed": state["nli_gate_passed"]})
    
    if state["nli_gate_passed"]:
        state["final_output"] = state["generated_answer"]
        
    return state


async def fallback_and_hitl_node(state: AegisExecutionState) -> AegisExecutionState:
    """Node 4: Non-LLM Fallback & Human-In-The-Loop Escalation when NLI score < 0.90."""
    logger.warning("NLI Gate Failed (<0.90). Triggering Non-LLM Fallback & HITL Escalation!")
    state["final_output"] = (
        "CIRCUIT FALLBACK: Generated response failed >90% NLI faithfulness threshold. "
        "Direct Citation: March 2024 Amendment Section 2.04 caps Restricted Subsidiary debt at $2,000,000. "
        "Escalated to Senior Risk Officer (Ticket: HITL-AEGIS-104)."
    )
    return state


# ---------------------------------------------------------------------------
# CONDITIONAL ROUTING & GRAPH COMPILATION
# ---------------------------------------------------------------------------

def route_after_nli_gate(state: AegisExecutionState) -> str:
    return "END" if state["nli_gate_passed"] else "fallback_and_hitl_node"


def build_aegis_state_machine():
    builder = StateGraph(AegisExecutionState)
    
    builder.add_node("parallel_retrieval_node", parallel_retrieval_node)
    builder.add_node("llm_generation_node", llm_generation_node)
    builder.add_node("local_nli_faithfulness_node", local_nli_faithfulness_node)
    builder.add_node("fallback_and_hitl_node", fallback_and_hitl_node)
    
    builder.set_entry_point("parallel_retrieval_node")
    builder.add_edge("parallel_retrieval_node", "llm_generation_node")
    builder.add_edge("llm_generation_node", "local_nli_faithfulness_node")
    
    builder.add_conditional_edges(
        "local_nli_faithfulness_node",
        route_after_nli_gate,
        {"END": END, "fallback_and_hitl_node": "fallback_and_hitl_node"}
    )
    builder.add_edge("fallback_and_hitl_node", END)
    
    return builder.compile()