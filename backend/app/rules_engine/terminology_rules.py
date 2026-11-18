
import re
from typing import Any


def analyze_preferred_terms(
    content: str,
    rules: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Detect non-preferred terminology and recommend
    approved brand alternatives.

    Each rule should contain:
    - non_preferred_term
    - preferred_term
    - source_reference
    - severity (optional)
    """

    findings = []

    if not content or not content.strip():
        return findings

    for rule in rules:
        non_preferred = rule.get(
            "non_preferred_term", ""
        ).strip()

        preferred = rule.get(
            "preferred_term", ""
        ).strip()

        source_reference = rule.get(
            "source_reference", ""
        ).strip()

        # Skip incomplete rules.
        if not non_preferred or not preferred or not source_reference:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(non_preferred)
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
                "finding_type": "NON_PREFERRED_TERM",
                "severity": rule.get("severity", "MEDIUM"),
                "description": (
                    f"'{matched_text}' is not the preferred "
                    f"brand terminology. Use '{preferred}' instead."
                ),
                "evidence": matched_text,
                "source_reference": source_reference,
                "suggested_fix": (
                    f"Replace '{matched_text}' with '{preferred}'."
                ),
                "confidence": 1.0
            })

    return findings
