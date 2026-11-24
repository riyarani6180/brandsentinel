
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.models.guideline import Guideline
from app.models.approved_fact import ApprovedFact
from app.models.review_submission import ReviewSubmission
from app.models.review_finding import ReviewFinding

from app.rules_engine.guideline_parser import extract_brand_rules
from app.rules_engine.text_rules import analyze_banned_terms
from app.rules_engine.terminology_rules import analyze_preferred_terms
from app.rules_engine.context_analyzer import analyze_submission_context
from app.rules_engine.risk_classifier import classify_submission_risk

from app.claims_ledger.claims_verifier import verify_claims

from app.ai_engine.semantic_analyzer import analyze_submission_semantics
from app.ai_engine.contradiction_detector import detect_contradictions
from app.ai_engine.misleading_claim_detector import detect_misleading_claims
from app.ai_engine.confidence_score import score_finding

from app.services.explainability_service import explain_findings


PERSISTABLE_FINDING_FIELDS = {
    "finding_type",
    "severity",
    "description",
    "evidence",
    "source_reference",
    "suggested_fix",
    "confidence",
    "verification_status",
}


def calculate_risk_score(findings: list[dict]) -> int:
    """Retain the original risk calculation for compatibility."""

    severity_weights = {
        "CRITICAL": 40,
        "HIGH": 25,
        "MEDIUM": 15,
        "LOW": 5,
    }

    score = sum(
        severity_weights.get(
            str(finding.get("severity", "LOW")).upper(),
            5,
        )
        for finding in findings
    )

    return min(score, 100)


def _normalize_text(value: Any) -> str:
    """Normalize text for reliable evidence comparison."""

    return " ".join(str(value or "").split()).casefold()


def _is_duplicate_contradiction(
    new_finding: dict,
    existing_findings: list[dict],
) -> bool:
    """Avoid duplicate numerical contradiction findings."""

    evidence = str(new_finding.get("evidence") or "")

    approved_fact = None

    for line in evidence.splitlines():

        if line.strip().lower().startswith("approved fact:"):
            approved_fact = line.split(":", 1)[1].strip()
            break

    if not approved_fact:
        return False

    normalized_fact = _normalize_text(approved_fact)

    for existing in existing_findings:

        if (
            str(existing.get("finding_type", "")).upper()
            != "CLAIM_VERIFICATION"
        ):
            continue

        if (
            str(existing.get("verification_status", "")).upper()
            != "CONTRADICTED"
        ):
            continue

        if (
            _normalize_text(existing.get("evidence"))
            == normalized_fact
        ):
            return True

    return False


def _find_context_for_finding(
    finding: dict,
    context_results: list[dict],
) -> dict | None:
    """Match a finding to its corresponding submitted sentence."""

    evidence = _normalize_text(finding.get("evidence"))

    if not evidence:
        return None

    for context in context_results:

        sentence = _normalize_text(context.get("sentence"))

        if not sentence:
            continue

        if evidence == sentence:
            return context

        if f"submitted claim: {sentence}" in evidence:
            return context

    return None


def _assign_verification_status(finding: dict) -> dict:
    """
    Assign a meaningful status when a detector does not provide one.

    Existing verification statuses are preserved.
    """

    result = finding.copy()

    existing_status = result.get("verification_status")

    if existing_status and str(existing_status).strip():
        return result

    finding_type = str(
        result.get("finding_type", "")
    ).upper()

    status_mapping = {
        "BANNED_TERM": "VIOLATION_DETECTED",
        "PREFERRED_TERMINOLOGY": "TERMINOLOGY_REVIEW",
        "NUMERICAL_CONTRADICTION": "CONTRADICTED",
        "MISLEADING_CLAIM": "REQUIRES_REVIEW",
        "CLAIM_VERIFICATION": "UNVERIFIED",
    }

    result["verification_status"] = status_mapping.get(
        finding_type,
        "REQUIRES_REVIEW",
    )

    return result


def _prepare_findings_for_database(
    findings: list[dict],
) -> list[dict]:
    """Remove analysis-only fields before database insertion."""

    prepared = []

    for finding in findings:

        database_finding = {
            key: value
            for key, value in finding.items()
            if key in PERSISTABLE_FINDING_FIELDS
        }

        prepared.append(database_finding)

    return prepared


def analyze_submission(
    db: Session,
    submission_id: int,
) -> dict[str, Any]:
    """Run the complete BrandSentinel compliance analysis."""

    submission = (
        db.query(ReviewSubmission)
        .filter(ReviewSubmission.id == submission_id)
        .first()
    )

    if not submission:
        raise ValueError("Review submission not found")

    # -------------------------------------------------
    # 1. Load active brand guidelines
    # -------------------------------------------------

    guidelines = (
        db.query(Guideline)
        .filter(Guideline.is_active.is_(True))
        .all()
    )

    all_findings = []

    # -------------------------------------------------
    # 2. Guideline and terminology analysis
    # -------------------------------------------------

    for guideline in guidelines:

        extracted_rules = extract_brand_rules(
            guideline.content
        )

        banned_findings = analyze_banned_terms(
            submission.content,
            extracted_rules["banned_terms"],
        )

        terminology_findings = analyze_preferred_terms(
            submission.content,
            extracted_rules["preferred_terms"],
        )

        all_findings.extend(banned_findings)
        all_findings.extend(terminology_findings)

    # -------------------------------------------------
    # 3. Load active and valid approved brand facts
    # -------------------------------------------------

    approved_facts = (
        db.query(ApprovedFact)
        .filter(ApprovedFact.is_active.is_(True))
        .filter(
            (ApprovedFact.valid_until.is_(None))
            | (ApprovedFact.valid_until >= date.today())
        )
        .all()
    )

    fact_data = [
        {
            "fact_content": fact.fact_content,
            "source_reference": fact.source_reference,
        }
        for fact in approved_facts
    ]

    # -------------------------------------------------
    # 4. Existing approved-fact verification
    # -------------------------------------------------

    claim_findings = verify_claims(
        submission.content,
        fact_data,
    )

    all_findings.extend(claim_findings)

    # -------------------------------------------------
    # 5. Semantic comparison
    # -------------------------------------------------

    semantic_matches = []
    semantic_analysis_status = "NOT_AVAILABLE"

    try:

        semantic_matches = analyze_submission_semantics(
            submission_text=submission.content,
            approved_facts=fact_data,
            top_k=3,
        )

        semantic_analysis_status = "COMPLETED"

    except Exception:
        # Rule-based checks continue even if the semantic model fails.
        semantic_analysis_status = "UNAVAILABLE"

    # -------------------------------------------------
    # 6. Numerical contradiction detection
    # -------------------------------------------------

    numerical_findings = detect_contradictions(
        semantic_matches,
        similarity_threshold=0.70,
    )

    for finding in numerical_findings:

        if not _is_duplicate_contradiction(
            finding,
            claim_findings,
        ):
            all_findings.append(finding)

    # -------------------------------------------------
    # 7. Misleading promotional claim detection
    # -------------------------------------------------

    misleading_findings = detect_misleading_claims(
        submission.content
    )

    all_findings.extend(misleading_findings)

    # -------------------------------------------------
    # 8. Context-aware analysis
    # -------------------------------------------------

    context_results = analyze_submission_context(
        submission.content,
        context_window=1,
    )

    # -------------------------------------------------
    # 9. Verification status, confidence and context
    # -------------------------------------------------

    scored_findings = []

    for finding in all_findings:

        normalized_finding = _assign_verification_status(
            finding
        )

        scored = score_finding(normalized_finding)

        context = _find_context_for_finding(
            scored,
            context_results,
        )

        if context:

            scored["context_status"] = context.get(
                "context_status"
            )

            scored["context_requires_review"] = context.get(
                "requires_human_review",
                False,
            )

            scored["has_qualifying_language"] = context.get(
                "has_qualifying_language"
            )

            scored["has_evidence_reference"] = context.get(
                "has_evidence_reference"
            )

        else:

            scored["context_status"] = None
            scored["context_requires_review"] = False
            scored["has_qualifying_language"] = None
            scored["has_evidence_reference"] = None

        scored_findings.append(scored)

    # -------------------------------------------------
    # 10. Explainable risk classification
    # -------------------------------------------------

    risk_analysis = classify_submission_risk(
        scored_findings
    )

    risk_score = risk_analysis["risk_score"]

    # -------------------------------------------------
    # 11. Human-readable explanations
    # -------------------------------------------------

    explanation_results = explain_findings(
        scored_findings
    )

    # -------------------------------------------------
    # 12. Determine submission status
    # -------------------------------------------------

    if risk_score >= 60:

        submission.status = "REQUIRES_REVIEW"

    elif risk_score > 0:

        submission.status = "NEEDS_REVISION"

    else:

        submission.status = "PASSED"

    submission.risk_score = risk_score

    # -------------------------------------------------
    # 13. Save findings safely
    # -------------------------------------------------

    database_findings = _prepare_findings_for_database(
        scored_findings
    )

    saved_findings = []

    try:

        db.query(ReviewFinding).filter(
            ReviewFinding.submission_id == submission.id
        ).delete(synchronize_session=False)

        for finding_data in database_findings:

            finding = ReviewFinding(
                submission_id=submission.id,
                **finding_data,
            )

            db.add(finding)
            saved_findings.append(finding)

        db.commit()

        for finding in saved_findings:
            db.refresh(finding)

        db.refresh(submission)

    except Exception:

        db.rollback()
        raise

    # -------------------------------------------------
    # 14. Build API response
    # -------------------------------------------------

    response_findings = []

    for index, finding in enumerate(saved_findings):

        analysis_finding = scored_findings[index]

        response_findings.append({
            "id": finding.id,
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "description": finding.description,
            "evidence": finding.evidence,
            "source_reference": finding.source_reference,
            "suggested_fix": finding.suggested_fix,
            "confidence": finding.confidence,
            "verification_status": finding.verification_status,
            "context_status": analysis_finding.get(
                "context_status"
            ),
            "confidence_level": analysis_finding.get(
                "confidence_level"
            ),
            "context_requires_review": analysis_finding.get(
                "context_requires_review"
            ),
            "has_qualifying_language": analysis_finding.get(
                "has_qualifying_language"
            ),
            "has_evidence_reference": analysis_finding.get(
                "has_evidence_reference"
            ),
        })

    # -------------------------------------------------
    # 15. Return complete analysis
    # -------------------------------------------------

    return {
        "submission_id": submission.id,
        "title": submission.title,
        "status": submission.status,
        "risk_score": submission.risk_score,
        "total_findings": len(saved_findings),
        "risk_analysis": risk_analysis,
        "semantic_analysis_status": semantic_analysis_status,
        "semantic_matches": semantic_matches,
        "context_analysis": context_results,
        "explainability": explanation_results,
        "findings": response_findings,
    }
