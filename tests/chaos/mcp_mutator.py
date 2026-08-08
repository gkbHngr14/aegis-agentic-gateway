"""
MCP Mutator: Generates malformed tool schemas, protocol latency hangs,
and context-flooding payloads to stress-test the DynamicToolRegistry.
"""

import asyncio
from typing import Dict, Any, List


class MCPMutator:

    @staticmethod
    def generate_corrupted_schemas() -> List[Dict[str, Any]]:
        """Generates schema payloads with structural and type anomalies."""
        return [
            # 1. Missing 'name' field
            {
                "type": "MISSING_NAME",
                "schema": {
                    "description": "Valid description without name",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            # 2. Invalid parameter types
            {
                "type": "INVALID_TYPE_MUTATION",
                "schema": {
                    "name": "fhir_query",
                    "description": "Queries patient FHIR records",
                    "parameters": "NOT_A_DICTIONARY",  # Should be dict
                },
            },
            # 3. Deeply nested recursive property bloat
            {
                "type": "DEEP_NESTING_EXHAUSTION",
                "schema": {
                    "name": "recursive_tool",
                    "description": "Deeply nested JSON schema",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "level_1": {
                                "type": "object",
                                "properties": {
                                    "level_2": {
                                        "type": "object",
                                        "properties": {"level_3": "CORRUPTED"},
                                    }
                                },
                            }
                        },
                    },
                },
            },
            # 4. Null payload injection
            {"type": "NULL_SCHEMA_PAYLOAD", "schema": None},
        ]

    @staticmethod
    def generate_context_flood(num_tools: int = 500) -> Dict[str, Any]:
        """Generates an oversized registry payload to test vector pruning."""
        flooded_registry = {}
        for i in range(num_tools):
            flooded_registry[f"synthetic_tool_{i}"] = {
                "name": f"synthetic_tool_{i}",
                "description": f"Synthetic tool description bloat item number {i} " * 20,
                "parameters": {"type": "object", "properties": {"arg": {"type": "string"}}},
            }
        return flooded_registry

    @staticmethod
    async def simulate_hanging_tool_call(timeout_seconds: float = 5.0) -> None:
        """Simulates an unresponsive downstream MCP server hang."""
        await asyncio.sleep(timeout_seconds)