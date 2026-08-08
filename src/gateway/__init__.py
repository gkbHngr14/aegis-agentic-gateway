"""
Gateway Package: Enterprise Federation Orchestrator, non-blocking sidecar ingress,
Vector Tool RAG (MCP Registry), and local DeBERTa NLI guardrails.
"""

from .sidecar_ingress import IngressContext, SecurityGatewaySidecar
from .mcp_registry import DynamicToolRegistry
from .nli_guardrail import LocalGuardrailEngine
from .aegis_federation_gateway import AegisFederationGateway

__all__ = [
    "IngressContext",
    "SecurityGatewaySidecar",
    "DynamicToolRegistry",
    "LocalGuardrailEngine",
    "AegisFederationGateway",
]