"""
Dynamic Tool Registry (MCP RAG): Resilient tool registry with recursive schema
depth validation, async timeout enforcement, and top-K semantic context pruning.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("Aegis.MCPRegistry")


class DynamicToolRegistry:

    def __init__(self, max_context_tools: int = 3, lookup_timeout_ms: float = 50.0, max_schema_depth: int = 2):
        self.max_context_tools = max_context_tools
        self.lookup_timeout_ms = lookup_timeout_ms
        self.max_schema_depth = max_schema_depth
        self._raw_registry: Dict[str, Dict[str, Any]] = {
            "query_fhir_patient_record": {
                "name": "query_fhir_patient_record",
                "description": "Retrieves clinical patient history from FHIR store.",
                "parameters": {"type": "object", "properties": {"patient_id": {"type": "string"}}},
            },
            "check_formulary_compliance": {
                "name": "check_formulary_compliance",
                "description": "Verifies insurance coverage and medication compliance.",
                "parameters": {"type": "object", "properties": {"medication_id": {"type": "string"}}},
            },
        }

    def _validate_properties_depth(self, node: Any, current_depth: int) -> bool:
        """Recursively checks property structures and rejects deep nesting or corrupted leaf nodes."""
        if current_depth > self.max_schema_depth:
            return False

        if not isinstance(node, dict):
            return False

        if "properties" in node:
            props = node["properties"]
            if not isinstance(props, dict):
                return False

            for _, prop_def in props.items():
                if not isinstance(prop_def, dict):
                    return False
                if prop_def.get("type") == "object":
                    if not self._validate_properties_depth(prop_def, current_depth + 1):
                        return False

        return True

    def validate_tool_schema(self, tool_id: str, schema: Any) -> bool:
        """Defensive schema validation: Rejects malformed JSON-RPC tool definitions."""
        if not isinstance(schema, dict):
            logger.warning(f"[MCP REGISTRY REJECT] Schema for '{tool_id}' is not a dict")
            return False

        if "name" not in schema or not isinstance(schema.get("name"), str):
            logger.warning(f"[MCP REGISTRY REJECT] Tool '{tool_id}' missing valid 'name'")
            return False

        if "parameters" in schema:
            params = schema["parameters"]
            if not isinstance(params, dict):
                logger.warning(f"[MCP REGISTRY REJECT] Tool '{tool_id}' has invalid 'parameters'")
                return False

            if not self._validate_properties_depth(params, current_depth=0):
                logger.warning(f"[MCP REGISTRY REJECT] Tool '{tool_id}' exceeded max depth or contains malformed property spec")
                return False

        return True

    def register_tool(self, tool_id: str, schema: Any) -> bool:
        """Safely registers a new tool schema into the local registry."""
        if self.validate_tool_schema(tool_id, schema):
            self._raw_registry[tool_id] = schema
            return True
        return False

    async def retrieve_relevant_tools(self, prompt: str) -> Dict[str, Dict[str, Any]]:
        """Retrieves top-K relevant tools within a strict timeout budget."""
        try:
            return await asyncio.wait_for(
                self._execute_retrieval(prompt),
                timeout=self.lookup_timeout_ms / 1000.0,
            )
        except asyncio.TimeoutError:
            logger.error(f"[MCP REGISTRY TIMEOUT] Retrieval exceeded {self.lookup_timeout_ms}ms! Falling back to default tools.")
            return {"query_fhir_patient_record": self._raw_registry["query_fhir_patient_record"]}

    async def _execute_retrieval(self, prompt: str) -> Dict[str, Dict[str, Any]]:
        """Simulates vector RAG top-K tool selection with strict context pruning."""
        valid_tools = {}

        for tool_id, schema in self._raw_registry.items():
            if self.validate_tool_schema(tool_id, schema):
                valid_tools[tool_id] = schema

            if len(valid_tools) >= self.max_context_tools:
                break

        return valid_tools