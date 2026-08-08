"""
NLI Mutator: Generates borderline hallucinations, numerical mutations,
and artificial inference delays to stress-test the Egress Guardrail Engine.
"""

from typing import List, Dict, Any


class NLIMutator:

    @staticmethod
    def generate_nli_probes() -> List[Dict[str, Any]]:
        return [
            # 1. Fully Faithful Claim (High Entailment >= 0.90)
            {
                "type": "FAITHFUL_CLAIM",
                "context": "Patient prescribed 10mg Lisinopril daily for hypertension.",
                "candidate": "The patient is taking 10mg of Lisinopril daily.",
                "simulate_delay_ms": 0.0,
                "expected_pass": True,
            },
            # 2. Numerical Mutation / Hallucination (Dosage mismatch -> Blocked)
            {
                "type": "NUMERICAL_MUTATION",
                "context": "Patient prescribed 10mg Lisinopril daily for hypertension.",
                "candidate": "The patient is taking 100mg of Lisinopril daily.",
                "simulate_delay_ms": 0.0,
                "expected_pass": False,
            },
            # 3. Severe Factual Contradiction (Blocked)
            {
                "type": "FACTUAL_CONTRADICTION",
                "context": "Patient has no known drug allergies.",
                "candidate": "Patient experienced a severe anaphylactic reaction to Penicillin.",
                "simulate_delay_ms": 0.0,
                "expected_pass": False,
            },
            # 4. Latency SLA Breach (50ms delay > 25ms SLA -> Heuristic Fallback)
            {
                "type": "SLA_TIMEOUT_FALLBACK",
                "context": "Patient vitals are within normal reference ranges.",
                "candidate": "All patient vitals are completely normal.",
                "simulate_delay_ms": 50.0,
                "expected_pass": True,  # Passes via Heuristic Fallback
            },
        ]