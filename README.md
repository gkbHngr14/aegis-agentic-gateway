# 🛡️ Project Aegis: Zero-Trust Agentic Security Gateway

[![Aegis Chaos CI](https://github.com/gkbHngr14/beast-agentic-platform/actions/workflows/aegis_chaos_gate.yml/badge.svg)](https://github.com/gkbHngr14/beast-agentic-platform/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Sub-millisecond Zero-Trust Security Sidecar, Tenant-Isolated Token Vault, and MCP Protocol Resiliency Gateway for Enterprise LLM Platforms.**

**Project Aegis** is an enterprise-grade, high-throughput security gateway designed to sit between client ingress traffic, Agentic orchestrators, and Model Context Protocol (MCP) tool integrations. Built for multi-tenant healthcare and fintech applications, Aegis enforces strict zero-trust boundary controls, sub-millisecond PII/PHI obfuscation, and NLI-driven output faithfulness verification while maintaining ultra-low SLA latency constraints.

---

## 🏛️ System Architecture

```text
                     ┌────────────────────────────────────────────────────────┐
                     │            INGRESS INSTRUCTION & DATA FLOW             │
                     └────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. INGRESS SECURITY SIDECAR (<0.1ms)                                                             │
│    - Obfuscation Normalizer (Zero-Width, Cyrillic Homoglyphs, Base64 Unpacking)                  │
│    - Inline Regex & Heuristic Short-Circuit Guard                                                │
│    - Attribute-Based Access Control (ABAC) Tenant Partitioning                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. TENANT-ISOLATED EPHEMERAL TOKEN VAULT (Redis / Dragonfly Key-Space)                           │
│    - Sub-millisecond PII/PHI Tokenization ([PATIENT_TOKEN_XXXX])                                 │
│    - Hard Key-Space Partitioning: `vault:{tenant_id}:{trace_id}:{token_hash}`                    │
│    - Native Auto-Eviction: TTL = 30 seconds | ABAC Role-Scoped Re-hydration                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. DYNAMIC MCP TOOL REGISTRY & PROTOCOL GATEWAY                                                  │
│    - Recursive JSON Schema Depth Validation (Max Depth = 2)                                      │
│    - Vector Top-K Context Pruning (Prunes 500+ synthetic tools -> Top 3)                          │
│    - Async Execution Timeout Circuit Breaker (<50ms budget)                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                                      ┌──────────────────────┐
                                      │  LLM / AGENT ENGINE  │
                                      └──────────────────────┘
                                                  │
                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. EGRESS NLI FAITHFULNESS GUARDRAIL                                                             │
│    - DeBERTa-v3 Cross-Encoder Entailment Scoring (Threshold >= 0.90)                            │
│    - Unit-Agnostic Numerical Sanity Engine (`10mg` vs `100mg` verification)                      │
│    - 25ms SLA Timeout Guardrail -> Sub-ms Lexical Overlap Fallback Engine                         │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

⚡️ Automated Chaos Release Gate (agenticChaosTester)
Aegis includes an automated, deterministic 4-Vector Red-Team Chaos Engine (tests/chaos/test_aegis_chaos.py) that acts as an automated release gate in CI/CD pipelines.

# Execute the full 4-Vector Chaos Suite locally (typical execution: ~0.07s)
python3 -m pytest tests/chaos/test_aegis_chaos.py -v

🚀 Quick Start & Local Execution
Prerequisites
Python 3.10+

Redis / Dragonfly (Optional; system defaults to sub-millisecond in-memory engine if Redis is offline)

Installation

# Clone the repository
git clone [https://github.com/gkbHngr14/beast-agentic-platform.git](https://github.com/gkbHngr14/beast-agentic-platform.git)
cd beast-agentic-platform

# Install dependencies
pip install pytest pytest-asyncio

Running the Chaos Gate & Unit Tests

# Run the complete Agentic Chaos Suite
python3 -m pytest tests/chaos/test_aegis_chaos.py -v -m chaos

# Output:
# tests/chaos/test_aegis_chaos.py::test_vector_1_security_injections PASSED [ 25%]
# tests/chaos/test_aegis_chaos.py::test_vector_2_tenant_privacy_vault PASSED [ 50%]
# tests/chaos/test_aegis_chaos.py::test_vector_3_mcp_protocol_chaos PASSED    [ 75%]
# tests/chaos/test_aegis_chaos.py::test_vector_4_nli_guardrail_sla PASSED    [100%]
# ============================= 4 passed in 0.07s =============================

🔒 Enterprise Compliance & Architecture Posture
HIPAA / HITECH Compliance: Zero raw PHI/PII leaves the enterprise boundary. All sensitive entities are tokenized at ingress, stored in hard-partitioned ephemeral key-spaces, and automatically purged after 30 seconds.

SOC2 Type II Auditability: Every blocked injection attempt, tenant access violation, and re-hydration event emits a WORM-compliant (Write-Once, Read-Many) audit log event.

Zero-Trust Network Architecture (ZTNA): Re-hydration requires explicit Attribute-Based Access Control (ABAC) role verification (clinician or phi_admin role required) tied to the requesting tenant context.

📄 License
Distributed under the MIT License. See LICENSE for more information.


---

With this `README.md` in place, pushing your repository creates a polished technical artifact. 

<ElicitationsGroup message="Now that the repo setup is ready, where should we focus our FDE GTM &amp; pipeline strategy today?">

{/* Reason: Offers clear next steps for shifting from code to pipeline generation, outreach strategy, and role positioning. */}

  <Elicitation label="Audit &amp; Position Portfolio Assets for FDE Outreach" query="Let's audit my background (PayPal, distributed systems, Aegis) and position it as a killer FDE value proposition."/>
  <Elicitation label="Build an Active Outbound Strategy for FDE &amp; Advisory Pipeline" query="Let's map out an active outbound pipeline generation strategy targeting AI consultancies, Series B/C startups, and enterprise clients."/>
  <Elicitation label="Draft Pitch Messages &amp; LinkedIn/Resume Narrative for FDE Roles" query="Let's draft concise pitch messages and update my LinkedIn/resume summary to frame me as a Lead FDE / Principal Architect."/>
</ElicitationsGroup>