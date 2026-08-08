"""
Prompt Injection Filter: High-throughput, sub-millisecond security filter
with Unicode normalization, homoglyph translation, and inline Base64 decoding.
"""

import base64
import re
import unicodedata
from typing import Optional, Tuple


class PromptInjectionFilter:

    # Homoglyph map: translates Cyrillic/Greek lookalikes to ASCII equivalents
    HOMOGLYPH_MAP = str.maketrans({
        'а': 'a', 'с': 'c', 'е': 'e', 'о': 'o', 'р': 'r', 'х': 'x', 'у': 'y', 'і': 'i', 'ј': 'j',
        'А': 'A', 'В': 'B', 'Е': 'E', 'К': 'K', 'М': 'M', 'Н': 'H', 'О': 'O', 'Р': 'P', 'С': 'C', 'Т': 'T', 'Х': 'X'
    })

    # Structural injection signatures & jailbreak patterns
    PATTERNS = [
        re.compile(r"ignore\s+all\s+previous\s+instructions", re.IGNORECASE),
        re.compile(r"dan\s+mode", re.IGNORECASE),
        re.compile(
            r"reveal\s+system\s+prompt|dump\s+all\s+mrns|override\s+safety\s+filters",
            re.IGNORECASE,
        ),
        re.compile(r"drop\s+table|select\s+\*\s+from|delete\s+from", re.IGNORECASE),
    ]

    @classmethod
    def normalize_input(cls, text: str) -> str:
        """Unmasks obfuscated attack payloads in sub-millisecond budgets."""
        # 1. Strip Zero-Width and Non-Printable Stealth Unicode Characters
        text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)

        # 2. NFKC Unicode Normalization (Fullwidth -> Standard)
        text = unicodedata.normalize("NFKC", text)

        # 3. Explicit Homoglyph Translation (Cyrillic -> Latin ASCII)
        text = text.translate(cls.HOMOGLYPH_MAP)

        # 4. Base64 Sniffing & Inline Payload Unpacking
        b64_matches = re.findall(r"[A-Za-z0-9+/]{16,}={0,2}", text)
        decoded_fragments = []
        for match in b64_matches:
            try:
                decoded = base64.b64decode(match).decode("utf-8", errors="ignore")
                if len(decoded) > 5:
                    decoded_fragments.append(decoded)
            except Exception:
                pass

        if decoded_fragments:
            text += " " + " ".join(decoded_fragments)

        return text

    @classmethod
    def inspect(cls, prompt: str) -> Tuple[bool, Optional[str]]:
        """Scans prompt text against known attack signatures after normalization."""
        normalized_prompt = cls.normalize_input(prompt)

        for pattern in cls.PATTERNS:
            if pattern.search(normalized_prompt):
                return (
                    False,
                    "SECURITY_VIOLATION: Prompt Injection / Jailbreak attempt detected.",
                )

        return True, None