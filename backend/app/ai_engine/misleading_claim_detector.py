
"""
BrandSentinel - Misleading Claim Detector

Detects potentially misleading promotional language
using explainable, deterministic rule-based patterns.

A detected phrase is a review signal, not proof
that the underlying claim is false.
"""

import re


# Each rule contains:
# pattern, category, severity, description, suggested fix
MISLEADING_RULES = [
    (
        r"\b(100%\s*safe|completely safe|totally safe|zero risk|risk[- ]free)\b",
        "ABSOLUTE_SAFETY_CLAIM",
        "HIGH",
        "The content makes an absolute safety or risk-free claim.",
        "Provide reliable evidence for the safety claim or use qualified wording."
    ),
    (
        r"\b(cures?|cure[- ]all|guaranteed to cure|permanently eliminates?)\b",
        "UNSUPPORTED_HEALTH_CLAIM",
        "HIGH",
        "The content may make an unsupported medical or treatment claim.",
        "Verify the claim against authorised clinical and regulatory evidence."
    ),
    (
        r"\b(no side effects|zero side effects|without any side effects)\b",
        "ABSOLUTE_HEALTH_CLAIM",
        "HIGH",
        "The content makes an absolute claim about the absence of side effects.",
        "Use evidence-backed, appropriately qualified wording."
    ),
    (
        r"\b(guaranteed results|instant results|permanent results|"
        r"works instantly|100%\s*effective)\b",
        "GUARANTEED_RESULT_CLAIM",
        "HIGH",
        "The content promises guaranteed or absolute results.",
        "Provide supporting evidence and clarify the conditions or limitations."
    ),
    (
        r"\b(best|number\s*1|no\.?\s*1|#1|fastest|"
        r"most effective|market leader|world's best)\b",
        "UNVERIFIED_SUPERLATIVE",
        "MEDIUM",
        "The content contains a comparative or superiority claim "
        "that may require supporting evidence.",
        "Provide a reliable comparison, ranking, or source for this claim."
    ),
    (
        r"\b(always works|never fails|works for everyone|"
        r"suitable for everyone|100%\s*success)\b",
        "ABSOLUTE_PERFORMANCE_CLAIM",
        "HIGH",
        "The content makes an absolute performance or success claim.",
        "Qualify the statement and provide supporting performance evidence."
    )
]


def extract_sentences(text: str) -> list[str]:
    """Split content into individual sentences."""

    if not text or not text.strip():
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def detect_misleading_claims(
    submitted_content: str
) -> list[dict]:
    """
    Detect potentially misleading claims.

    Evidence contains the exact matched phrase.
    Separate claim categories remain separate findings.
    """

    findings = []

    if not submitted_content or not submitted_content.strip():
        return findings

    sentences = extract_sentences(submitted_content)

    for sentence in sentences:

        detected_categories = set()

        for (
            pattern,
            category,
            severity,
            description,
            suggested_fix
        ) in MISLEADING_RULES:

            matches = list(
                re.finditer(
                    pattern,
                    sentence,
                    flags=re.IGNORECASE
                )
            )

            if not matches or category in detected_categories:
                continue

            detected_categories.add(category)

            # Keep only the matched phrase as evidence.
            matched_phrases = list(dict.fromkeys(
                match.group(0) for match in matches
            ))

            for phrase in matched_phrases:
                findings.append({
                    "finding_type": "MISLEADING_CLAIM",
                    "severity": severity,
                    "description": description,
                    "evidence": phrase,
                    "source_reference": None,
                    "suggested_fix": suggested_fix,
                    "confidence": 0.85,
                    "verification_status": "REQUIRES_REVIEW"
                })

    return findings
