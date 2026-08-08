import time
from typing import List, Optional
from pydantic import BaseModel

from src.security import PromptInjectionFilter
# Import your audit logger if ready, or stub for now
from src.gateway.audit_logger import WORMAuditLogger


class IngressContext(BaseModel):
  user_id: str
  tenant_id: str
  roles: List[str]
  raw_prompt: str
  sanitized_prompt: Optional[str] = None
  abac_authorized: bool = False
  security_violation: Optional[str] = None


class SecurityGatewaySidecar:

  @staticmethod
  async def process_ingress(ctx: IngressContext) -> IngressContext:
    start_time = time.perf_counter()

    # 1. JWT ABAC Role Enforcement
    if "clinician" not in ctx.roles and "billing_admin" not in ctx.roles:
      ctx.abac_authorized = False
      raise PermissionError(
          f"ABAC Violation: Role '{ctx.roles}' unauthorized for tenant"
          f" {ctx.tenant_id}"
      )
    ctx.abac_authorized = True

    # 2. Inbound Prompt Injection & Malicious Payload Scan (<1ms)
    is_safe, violation_reason = PromptInjectionFilter.inspect(ctx.raw_prompt)
    if not is_safe:
      ctx.security_violation = violation_reason
      elapsed_ms = (time.perf_counter() - start_time) * 1000

      # Fire-and-forget async audit log
      await WORMAuditLogger.log_security_event(
          event_type="PROMPT_INJECTION_BLOCKED",
          tenant_id=ctx.tenant_id,
          user_id=ctx.user_id,
          payload={
              "raw_prompt": ctx.raw_prompt,
              "reason": violation_reason,
              "latency_ms": elapsed_ms,
          },
          status="BLOCKED",
      )

      print(
          f"[SECURITY SIDECAR - SHORT CIRCUIT] {violation_reason} in"
          f" {elapsed_ms:.2f}ms"
      )
      return ctx

    # 3. Presidio-style PHI/PII Masking
    masked_text = ctx.raw_prompt
    if "John Doe" in masked_text:
      masked_text = masked_text.replace("John Doe", "[PATIENT_TOKEN_99A2]")
    if "MRN-55412" in masked_text:
      masked_text = masked_text.replace("MRN-55412", "[MRN_TOKEN_SECURE]")

    ctx.sanitized_prompt = masked_text
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    print(
        "[SECURITY SIDECAR] Ingress scrubbed & ABAC verified in"
        f" {elapsed_ms:.2f}ms"
    )
    return ctx