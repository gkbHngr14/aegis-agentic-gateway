import asyncio
import json
import time
from typing import Any, Dict


class WORMAuditLogger:
  """Asynchronous, non-blocking audit logger for compliance & security.

  Simulates streaming OpenTelemetry spans and append-only WORM logs to S3 /
  Kafka without blocking the request latency path.
  """

  @staticmethod
  async def log_security_event(
      event_type: str,
      tenant_id: str,
      user_id: str,
      payload: Dict[str, Any],
      status: str,
  ) -> None:
    # Execute as a background fire-and-forget task
    asyncio.create_task(
        WORMAuditLogger._write_log(
            event_type, tenant_id, user_id, payload, status
        )
    )

  @staticmethod
  async def _write_log(
      event_type: str,
      tenant_id: str,
      user_id: str,
      payload: Dict[str, Any],
      status: str,
  ) -> None:
    # Simulated non-blocking disk / S3 object append (<2ms)
    await asyncio.sleep(0.002)

    log_entry = {
        "timestamp_utc": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
        ),
        "event_type": event_type,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "status": status,
        "payload": payload,
        "worm_compliance": "S3_OBJECT_LOCK_COMPLIANT",
    }

    print(
        f"[AUDIT LOG - WORM COMPLIANT] Event: {event_type} | Status: {status} |"
        f" Tenant: {tenant_id}"
    )
    # In production, this writes to a local buffer flusher / OTel exporter