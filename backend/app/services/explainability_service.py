
"""
BrandSentinel - Explainability Service

Generates deterministic, evidence-based explanations
using existing compliance detector outputs.

This service does not generate or invent evidence.
"""

SEVERITY_EXPLANATIONS = {
    "CRITICAL": "This issue may have a serious impact and needs immediate review.",
    "HIGH": "This issue may create significant compliance or brand-trust concerns.",
    "MEDIUM": "This issue may require clarification or supporting evidence.",
    "LOW": "This issue is relatively minor but should still be checked."
}

VERIFICATION_EXPLANATIONS = {
    "SUPPORTED": (
        "Supporting evidence was found in the approved facts ledger. "
        "This claim is supported by the available approved information."
    ),
    "UNVERIFIED": (
        "No sufficient approved supporting evidence was found. "
        "This does not mean the claim is false; additional verification is needed."
    ),
    "CONTRADICTED": (
        "The submitted claim conflicts with available approved evidence. "
        "A reviewer should examine the conflicting information."
    ),
    "REQUIRES_REVIEW": (
        "The automated checks could not reach a definitive conclusion. "
        "Human review is required."
    ),
    "VIOLATION_DETECTED": (
        "A defined compliance rule was violated based on the detected evidence."
    ),
    "UNKNOWN": (
        "The verification status is unknown. Additional assessment is required."
    )
}


def explain_finding(finding: dict) -> dict:
    """Generate a structured explanation for one finding."""

    finding_type = str(
        finding.get("finding_type", "GENERAL")
    ).upper()

    severity = str(
        finding.get("severity", "LOW")
    ).upper()

    verification_status = str(
        finding.get("verification_status", "REQUIRES_REVIEW")
    ).upper()

    evidence = finding.get("evidence")
    description = finding.get("description")
    suggested_fix = finding.get("suggested_fix")
    source_reference = finding.get("source_reference")
    confidence = finding.get("confidence")

    if finding_type == "MISLEADING_CLAIM":
        reason = (
            "A potentially misleading or absolute promotional "
            "statement was detected by the rule-based claim detector."
        )

    elif finding_type == "NUMERICAL_CONTRADICTION":
        reason = (
            "A numerical value in the submitted content differs "
            "from a semantically related approved brand fact."
        )

    elif finding_type == "UNVERIFIED_CLAIM":
        reason = (
            "The submitted claim could not be matched with "
            "sufficient approved supporting evidence."
        )

    else:
        reason = (
            description
            or "A compliance rule identified a potential issue."
        )

    severity_explanation = SEVERITY_EXPLANATIONS.get(
        severity,
        SEVERITY_EXPLANATIONS["LOW"]
    )

    verification_explanation = VERIFICATION_EXPLANATIONS.get(
        verification_status,
        VERIFICATION_EXPLANATIONS["UNKNOWN"]
    )

    return {
        "finding_type": finding_type,
        "severity": severity,
        "reason": reason,
        "severity_explanation": severity_explanation,
        "verification_explanation": verification_explanation,
        "evidence": evidence,
        "source_reference": source_reference,
        "suggested_fix": suggested_fix,
        "confidence": confidence,
        "verification_status": verification_status,
        "human_review_required": True
    }


def explain_findings(findings: list[dict]) -> dict:
    """Generate explanations for all findings in a submission."""

    explanations = [
        explain_finding(finding)
        for finding in findings
    ]

    return {
        "total_explanations": len(explanations),
        "explanations": explanations,
        "review_recommendation": (
            "Human review is recommended for all detected findings."
            if explanations
            else "No findings were supplied for explanation."
        )
    }
