
import re
from typing import Any


def normalize_text(text: str) -> str:
    """
    Normalize text for deterministic comparison.
    """

    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text


def extract_numeric_values(text: str) -> list[float]:
    """
    Extract numeric values from text.
    """

    matches = re.findall(
        r"\d+(?:\.\d+)?",
        text
    )

    return [float(value) for value in matches]


def extract_battery_life_claim(text: str):
    """
    Extract battery-life values from different sentence structures.

    Supported examples:
    - Battery life is up to 12 hours.
    - The battery lasts 8 hours.
    - The product provides up to 12 hours of battery life.
    """

    patterns = [
        # Battery life is up to 12 hours.
        r"(?:battery(?:\s+life)?|battery\s+backup)"
        r".{0,50}?(\d+(?:\.\d+)?)\s*hours?",

        # Up to 12 hours of battery life.
        r"(\d+(?:\.\d+)?)\s*hours?"
        r"\s+(?:of\s+)?battery(?:\s+life)?"
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            return float(match.group(1))

    return None


def verify_claims(
    submitted_content: str,
    approved_facts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Verify submitted claims against approved facts.

    Verification statuses:
    - SUPPORTED
    - CONTRADICTED
    - UNVERIFIED

    Currently supports:
    - Exact approved-fact matching.
    - Conservative battery-life numerical comparison.
    """

    findings = []

    if not submitted_content or not submitted_content.strip():
        return findings

    normalized_content = normalize_text(
        submitted_content
    )

    matched_fact_found = False
    contradiction_found = False

    for fact in approved_facts:

        fact_content = fact.get(
            "fact_content", ""
        ).strip()

        source_reference = fact.get(
            "source_reference"
        )

        if not fact_content or not source_reference:
            continue

        normalized_fact = normalize_text(
            fact_content
        )

        # Check exact approved-fact match.
        if normalized_fact in normalized_content:

            matched_fact_found = True

            findings.append({
                "finding_type": "CLAIM_VERIFICATION",
                "severity": "LOW",
                "description": (
                    "A submitted statement matches an approved fact."
                ),
                "evidence": fact_content,
                "source_reference": source_reference,
                "suggested_fix": (
                    "No correction required for this matched statement."
                ),
                "confidence": 1.0,
                "verification_status": "SUPPORTED"
            })

            continue

        # Extract battery-life values from both statements.
        approved_battery_hours = extract_battery_life_claim(
            fact_content
        )

        submitted_battery_hours = extract_battery_life_claim(
            submitted_content
        )

        # Compare only when both statements contain
        # recognizable battery-life measurements.
        if (
            approved_battery_hours is not None
            and submitted_battery_hours is not None
            and approved_battery_hours != submitted_battery_hours
        ):

            contradiction_found = True

            findings.append({
                "finding_type": "CLAIM_VERIFICATION",
                "severity": "HIGH",
                "description": (
                    "The submitted battery-life claim conflicts "
                    "with the approved product specification."
                ),
                "evidence": fact_content,
                "source_reference": source_reference,
                "suggested_fix": (
                    f"Verify the battery-life claim and use the "
                    f"approved value of {approved_battery_hours:g} hours."
                ),
                "confidence": 1.0,
                "verification_status": "CONTRADICTED"
            })

    # Report unverified content only when neither
    # supported nor contradicted evidence was found.
    if not matched_fact_found and not contradiction_found:

        findings.append({
            "finding_type": "CLAIM_VERIFICATION",
            "severity": "MEDIUM",
            "description": (
                "No exact supporting approved fact was found "
                "for the submitted content."
            ),
            "evidence": None,
            "source_reference": (
                "Approved Facts Ledger - No matching evidence found"
            ),
            "suggested_fix": (
                "Provide an approved source or ask an authorised "
                "reviewer to verify this claim."
            ),
            "confidence": 1.0,
            "verification_status": "UNVERIFIED"
        })

    return findings
