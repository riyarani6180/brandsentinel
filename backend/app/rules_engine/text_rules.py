
import re
from typing import Any


def analyze_banned_terms(
    content: str,
    rules: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Detect banned words and common word variations
    in submitted content.
    """

    findings = []

    if not content or not content.strip():
        return findings

    for rule in rules:
        term = rule.get("term", "").strip()
        source_reference = rule.get("source_reference", "").strip()

        if not term or not source_reference:
            continue

        escaped_term = re.escape(term)

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

            if term.lower() == "guaranteed":
                suggested_fix = (
                    f"Remove or replace the detected term "
                    f"'{matched_text}' with wording approved by the brand."
                )
            else:
                suggested_fix = rule.get(
                    "suggested_fix",
                    f"Remove or replace the banned term '{matched_text}'."
                )

            findings.append({
                "finding_type": "BANNED_TERM",
                "severity": rule.get("severity", "MEDIUM"),
                "description": (
                    f"The banned term '{matched_text}' "
                    "was detected in the submitted content."
                ),
                "evidence": matched_text,
                "source_reference": source_reference,
                "suggested_fix": suggested_fix,
                "confidence": 1.0
            })

    return findings
