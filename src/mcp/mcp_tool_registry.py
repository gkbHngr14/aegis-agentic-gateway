# ---------------------------------------------------------------------------
# 4. MODEL CONTEXT PROTOCOL (MCP) TOOL SCHEMAS
# ---------------------------------------------------------------------------
import math
import time
import random
import logging
from typing import Dict, List, Any, Optional  # <--- Added typing imports

logger = logging.getLogger("AegisMCPToolRegistry")

class AegisMCPToolRegistry:
    """Standardized JSON-RPC Tool Schemas for Model Context Protocol (MCP) Gateway."""

    @staticmethod
    def get_opensearch_mcp_schema() -> Dict[str, Any]:
        return {
            "name": "opensearch_hybrid_vector_search",
            "description": "Executes hybrid BM25 text + HNSW vector similarity search over credit agreement document chunks in OpenSearch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query string or legal clause keywords."},
                    "tenant_id": {"type": "string", "description": "Mandatory tenant isolation identifier."},
                    "abac_roles": {"type": "array", "items": {"type": "string"}, "description": "User ABAC roles to enforce document ACL filtering."},
                    "k": {"type": "integer", "default": 5, "description": "Number of top chunks to retrieve."}
                },
                "required": ["query", "tenant_id", "abac_roles"]
            }
        }

    @staticmethod
    def get_neptune_mcp_schema() -> Dict[str, Any]:
        return {
            "name": "neptune_cypher_graph_traversal",
            "description": "Traverses corporate entity ownership, cross-default guarantees, and superseding amendment edges in Amazon Neptune.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string", "description": "Target corporate entity (e.g., 'Subsidiary B')."},
                    "tenant_id": {"type": "string", "description": "Mandatory tenant isolation identifier."},
                    "max_hops": {"type": "integer", "default": 3, "description": "Maximum path traversal depth (bounded for sub-50ms SLA)."}
                },
                "required": ["entity_name", "tenant_id"]
            }
        }