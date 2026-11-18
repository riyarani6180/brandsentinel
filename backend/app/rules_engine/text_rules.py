
import re
from typing import Any


def analyze_banned_terms(
    content: str,
    rules: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Detect banned words and common word variations
    in submitted content.

    Each rule should contain:
    - term: Word or phrase to detect
    - source_reference: Guideline supporting the rule
    - suggested_fix: Recommended correction
    - severity: LOW, MEDIUM, HIGH, or CRITICAL
    """

    findings = []

    if not content or not content.strip():
        return findings

    for rule in rules:
        term = rule.get("term", "").strip()
        source_reference = rule.get("source_reference", "").strip()

        # Ignore incomplete rules.
        if not term or not source_reference:
            continue

        # Escape the term to safely handle special characters.
        escaped_term = re.escape(term)

        # Support common English variations of a single word.
        if " " not in term:
            if term.lower() == "guaranteed":
                pattern = r"(?<!\w)guarante(?:e|ed|es|eing)(?!\w)"
            else:
                pattern = (
                    r"(?<!\w)"
                    + escaped_term
                    + r"(?!\w)"
                )
        else:
            # Keep phrase matching exact.
            pattern = (
                r"(?<!\w)"
                + escaped_term
                + r"(?!\w)"
            )

        matches = re.finditer(
            pattern,
            content,
            flags=re.IGNORECASE
        )

        for match in matches:
            matched_text = match.group()

            findings.append({
                "finding_type": "BANNED_TERM",
                "severity": rule.get("severity", "MEDIUM"),
                "description": (
                    f"The banned term '{matched_text}' "
                    "was detected in the submitted content."
                ),
                "evidence": matched_text,
                "source_reference": source_reference,
                "suggested_fix": rule.get(
                    "suggested_fix",
                    "Remove or replace this term."
                ),
                "confidence": 1.0
            })

    return findings
