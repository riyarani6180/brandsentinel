
"""
BrandSentinel - Risk Classifier

Calculates an explainable submission risk score
from detected compliance findings.

Risk and confidence are separate:
- Confidence measures detection reliability.
- Severity measures potential impact.
- Risk score prioritizes review.
"""

SEVERITY_WEIGHTS = {
    "LOW": 10,
    "MEDIUM": 25,
    "HIGH": 40,
    "CRITICAL": 60
}

CONFIDENCE_THRESHOLD = 0.60


def clamp_score(score: float) -> int:
    """Keep risk score between 0 and 100."""
    return max(0, min(100, int(score + 0.5)))


def _get_confidence(finding: dict) -> float:
    """Safely normalize confidence to the range 0.0–1.0."""

    try:
        confidence = float(finding.get("confidence", 0.50))
    except (TypeError, ValueError):
        confidence = 0.50

    return max(0.0, min(1.0, confidence))


def calculate_finding_risk(finding: dict) -> float:
    """Calculate risk contribution from one finding."""

    severity = str(
        finding.get("severity", "LOW")
    ).upper()

    severity_weight = SEVERITY_WEIGHTS.get(
        severity, SEVERITY_WEIGHTS["LOW"]
    )

    confidence = _get_confidence(finding)

    verification_status = str(
        finding.get("verification_status", "")
    ).upper()

    # An unverified claim is a review signal, not a confirmed violation.
    if verification_status == "UNVERIFIED":
        severity_weight *= 0.50

    return severity_weight * confidence


def classify_risk_level(score: int) -> str:
    """Convert a numerical risk score into a risk category."""

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 30:
        return "MEDIUM"

    return "LOW"


def classify_submission_risk(findings: list[dict]) -> dict:
    """
    Calculate an overall risk score.

    Each finding contributes according to its severity
    and confidence. Multiple findings increase risk,
    but the total is capped at 100.
    """

    if not findings:
        return {
            "risk_score": 0,
            "risk_level": "LOW",
            "total_findings": 0,
            "high_confidence_findings": 0,
            "requires_human_review": False,
            "finding_risks": []
        }

    finding_risks = [
        round(calculate_finding_risk(finding), 2)
        for finding in findings
    ]

    risk_score = clamp_score(sum(finding_risks))

    high_confidence_count = sum(
        1
        for finding in findings
        if _get_confidence(finding) >= CONFIDENCE_THRESHOLD
    )

    risk_level = classify_risk_level(risk_score)

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "total_findings": len(findings),
        "high_confidence_findings": high_confidence_count,
        "requires_human_review": (
            risk_score >= 30 or len(findings) > 0
        ),
        "finding_risks": finding_risks
    }
