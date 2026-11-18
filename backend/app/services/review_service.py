
from datetime import date

from sqlalchemy.orm import Session

from app.models.guideline import Guideline
from app.models.approved_fact import ApprovedFact
from app.models.review_submission import ReviewSubmission
from app.models.review_finding import ReviewFinding

from app.rules_engine.guideline_parser import extract_brand_rules
from app.rules_engine.text_rules import analyze_banned_terms
from app.rules_engine.terminology_rules import analyze_preferred_terms

from app.claims_ledger.claims_verifier import verify_claims


def calculate_risk_score(findings: list[dict]) -> int:
    """
    Calculate submission risk score.

    CRITICAL = 40
    HIGH = 25
    MEDIUM = 15
    LOW = 5

    Maximum score = 100.
    """

    severity_weights = {
        "CRITICAL": 40,
        "HIGH": 25,
        "MEDIUM": 15,
        "LOW": 5
    }

    score = sum(
        severity_weights.get(
            finding.get("severity", "LOW").upper(), 5
        )
        for finding in findings
    )

    return min(score, 100)


def analyze_submission(
    db: Session,
    submission_id: int
) -> dict:
    """
    Analyse submitted content using brand guidelines
    and the approved facts ledger.
    """

    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == submission_id
    ).first()

    if not submission:
        raise ValueError("Review submission not found")

    guidelines = db.query(Guideline).filter(
        Guideline.is_active.is_(True)
    ).all()

    all_findings = []

    # Run brand guideline checks.
    for guideline in guidelines:

        extracted_rules = extract_brand_rules(
            guideline.content
        )

        banned_findings = analyze_banned_terms(
            submission.content,
            extracted_rules["banned_terms"]
        )

        terminology_findings = analyze_preferred_terms(
            submission.content,
            extracted_rules["preferred_terms"]
        )

        all_findings.extend(banned_findings)
        all_findings.extend(terminology_findings)

    # Retrieve active, non-expired approved facts.
    approved_facts = db.query(ApprovedFact).filter(
        ApprovedFact.is_active.is_(True)
    ).filter(
        (ApprovedFact.valid_until.is_(None)) |
        (ApprovedFact.valid_until >= date.today())
    ).all()

    fact_data = [
        {
            "fact_content": fact.fact_content,
            "source_reference": fact.source_reference
        }
        for fact in approved_facts
    ]

    # Verify claims against approved facts.
    claim_findings = verify_claims(
        submission.content,
        fact_data
    )

    all_findings.extend(claim_findings)

    # Calculate risk score.
    risk_score = calculate_risk_score(all_findings)

    # Delete previous findings for this submission
    # to prevent duplicate records during re-analysis.
    db.query(ReviewFinding).filter(
        ReviewFinding.submission_id == submission.id
    ).delete(synchronize_session=False)

    # Save the latest analysis findings.
    saved_findings = []

    for finding_data in all_findings:

        finding = ReviewFinding(
            submission_id=submission.id,
            **finding_data
        )

        db.add(finding)
        saved_findings.append(finding)

    # Update submission risk and review status.
    submission.risk_score = risk_score

    if risk_score >= 60:
        submission.status = "REQUIRES_REVIEW"
    elif risk_score > 0:
        submission.status = "NEEDS_REVISION"
    else:
        submission.status = "PASSED"

    # Save changes.
    db.commit()

    for finding in saved_findings:
        db.refresh(finding)

    db.refresh(submission)

    return {
        "submission_id": submission.id,
        "title": submission.title,
        "status": submission.status,
        "risk_score": submission.risk_score,
        "total_findings": len(saved_findings),
        "findings": [
            {
                "id": finding.id,
                "finding_type": finding.finding_type,
                "severity": finding.severity,
                "description": finding.description,
                "evidence": finding.evidence,
                "source_reference": finding.source_reference,
                "suggested_fix": finding.suggested_fix,
                "confidence": finding.confidence,
                "verification_status": finding.verification_status
            }
            for finding in saved_findings
        ]
    }
