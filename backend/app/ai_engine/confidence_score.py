
"""
BrandSentinel - Confidence Scorer

Calculates deterministic confidence scores for
compliance findings.

Confidence is not the same as severity or risk.
A high confidence score does not automatically
mean that a claim is false.
"""


def clamp_score(score: float) -> float:
    """Keep confidence between 0 and 1."""
    return round(max(0.0, min(1.0, score)), 2)


def calculate_confidence(
    finding: dict,
    semantic_similarity: float | None = None
) -> float:
    """
    Calculate confidence using the finding type
    and available supporting evidence.

    Returns a score between 0 and 1.
    """

    finding_type = finding.get("finding_type", "").upper()
    verification_status = finding.get(
        "verification_status", ""
    ).upper()

    # Exact approved-fact match.
    if verification_status == "SUPPORTED":
        return 0.98

    # Numerical contradiction supported by semantic matching.
    if finding_type == "NUMERICAL_CONTRADICTION":
        if semantic_similarity is not None:
            similarity = clamp_score(semantic_similarity)
            return clamp_score(0.80 + (similarity - 0.70) * 0.5)

        # Preserve an existing detector confidence if available.
        return clamp_score(finding.get("confidence", 0.80))

    # A recognised risky phrase matched a deterministic rule.
    if finding_type == "MISLEADING_CLAIM":
        return 0.85

    # No supporting evidence is not proof of a violation.
    if verification_status == "UNVERIFIED":
        return 0.40

    # For other finding types, preserve a supplied score.
    existing_score = finding.get("confidence")

    if existing_score is not None:
        try:
            return clamp_score(float(existing_score))
        except (TypeError, ValueError):
            pass

    # Neutral fallback when evidence is insufficient.
    return 0.50


def classify_confidence(score: float) -> str:
    """Convert a confidence score into an understandable label."""

    score = clamp_score(score)

    if score >= 0.85:
        return "HIGH"

    if score >= 0.60:
        return "MEDIUM"

    return "LOW"


def score_finding(
    finding: dict,
    semantic_similarity: float | None = None
) -> dict:
    """
    Return a finding enriched with its confidence score
    and confidence label.
    """

    result = finding.copy()

    confidence = calculate_confidence(
        finding,
        semantic_similarity
    )

    result["confidence"] = confidence
    result["confidence_level"] = classify_confidence(
        confidence
    )

    return result
