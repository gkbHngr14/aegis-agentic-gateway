"""
PROJECT AEGIS — OPENTELEMETRY TRACING ENGINE
Simulates OTLP Span Emission for TTFT Monitoring & S3 WORM Compliance Logs
"""

import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("AegisOTelTracer")


class OTelSpanTracer:
    """Simulates OpenTelemetry (OTLP) span emission for SLA and WORM audit logs."""
    
    def __init__(self, trace_id: str, tenant_id: str):
        self.trace_id = trace_id
        self.tenant_id = tenant_id
        self.spans: List[Dict[str, Any]] = []

    def record_span(self, name: str, duration_ms: float, attributes: Dict[str, Any]):
        """Records an OTLP trace span with metadata."""
        span = {
            "trace_id": self.trace_id,
            "tenant_id": self.tenant_id,
            "span_name": name,
            "duration_ms": round(duration_ms, 2),
            "attributes": attributes,
            "timestamp": time.time()
        }
        self.spans.append(span)
        logger.info(f"[OTel Span] {name} executed in {duration_ms:.2f}ms | Attrs: {attributes}")