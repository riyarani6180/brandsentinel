
import json
from collections import Counter
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.review_submission import ReviewSubmission
from app.models.review_finding import ReviewFinding
from app.models.audit_log import AuditLog
from app.services.explainability_service import explain_finding
from app.rules_engine.risk_classifier import classify_risk_level


def _date_filters(query, model, start_date=None, end_date=None):
    """Apply inclusive date filters."""

    if start_date:
        query = query.filter(
            model.created_at >= datetime.combine(
                start_date, time.min
            )
        )

    if end_date:
        query = query.filter(
            model.created_at < datetime.combine(
                end_date + timedelta(days=1), time.min
            )
        )

    return query


def _parse_audit_details(details):
    """Safely parse JSON audit details."""

    if not details:
        return None

    try:
        return json.loads(details)
    except (json.JSONDecodeError, TypeError):
        return {
            "raw_details": details,
            "parse_error": "Invalid JSON stored in audit log."
        }


def get_compliance_overview(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
) -> dict:
    """Generate deterministic organisation-wide compliance metrics."""

    submissions = _date_filters(
        db.query(ReviewSubmission),
        ReviewSubmission,
        start_date,
        end_date
    ).all()

    findings_query = db.query(ReviewFinding).join(
        ReviewSubmission,
        ReviewFinding.submission_id == ReviewSubmission.id
    )

    findings_query = _date_filters(
        findings_query,
        ReviewSubmission,
        start_date,
        end_date
    )

    findings = findings_query.all()

    total = len(submissions)

    status_counts = Counter(
        (submission.status or "UNKNOWN").upper()
        for submission in submissions
    )

    risk_distribution = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }

    for submission in submissions:
        score = submission.risk_score or 0
        level = classify_risk_level(score)
        risk_distribution[level] += 1

    finding_severity = Counter(
        (finding.severity or "UNKNOWN").upper()
        for finding in findings
    )

    finding_types = Counter(
        (finding.finding_type or "UNKNOWN").upper()
        for finding in findings
    )

    verification_statuses = Counter(
        (finding.verification_status or "UNKNOWN").upper()
        for finding in findings
    )

    confidence_values = [
        float(finding.confidence)
        for finding in findings
        if finding.confidence is not None
    ]

    average_confidence = (
        round(sum(confidence_values) / len(confidence_values), 3)
        if confidence_values else None
    )

    return {
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        },
        "submissions": {
            "total": total,
            "by_status": dict(status_counts),
            "approval_rate": round(
                status_counts.get("APPROVED", 0) / total * 100, 2
            ) if total else 0
        },
        "risk_distribution": risk_distribution,
        "findings": {
            "total": len(findings),
            "by_severity": dict(finding_severity),
            "by_type": dict(finding_types),
            "by_verification_status": dict(verification_statuses),
            "average_confidence": average_confidence
        }
    }


def get_submission_trends(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
) -> dict:
    """Group submissions by creation date."""

    query = _date_filters(
        db.query(ReviewSubmission),
        ReviewSubmission,
        start_date,
        end_date
    )

    submissions = query.all()

    daily_counts = Counter(
        submission.created_at.date().isoformat()
        for submission in submissions
        if submission.created_at is not None
    )

    return {
        "total_submissions": len(submissions),
        "daily_submissions": [
            {
                "date": day,
                "count": daily_counts[day]
            }
            for day in sorted(daily_counts)
        ]
    }


def get_explainable_report(
    db: Session,
    submission_id: int
) -> dict | None:
    """Generate an evidence-backed report for one submission."""

    submission = db.query(ReviewSubmission).filter(
        ReviewSubmission.id == submission_id
    ).first()

    if not submission:
        return None

    findings = db.query(ReviewFinding).filter(
        ReviewFinding.submission_id == submission_id
    ).order_by(ReviewFinding.id.asc()).all()

    finding_data = [
        {
            "id": finding.id,
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "description": finding.description,
            "evidence": finding.evidence,
            "source_reference": finding.source_reference,
            "suggested_fix": finding.suggested_fix,
            "confidence": finding.confidence,
            "verification_status": finding.verification_status,
            "status": finding.status
        }
        for finding in findings
    ]

    explanations = [
        {
            "finding_id": finding["id"],
            **explain_finding(finding)
        }
        for finding in finding_data
    ]

    return {
        "submission": {
            "id": submission.id,
            "title": submission.title,
            "channel": submission.channel,
            "submitted_by": submission.submitted_by,
            "status": submission.status,
            "risk_score": submission.risk_score,
            "created_at": (
                submission.created_at.isoformat()
                if submission.created_at else None
            )
        },
        "summary": {
            "total_findings": len(findings),
            "critical_findings": sum(
                1 for item in findings
                if (item.severity or "").upper() == "CRITICAL"
            ),
            "high_findings": sum(
                1 for item in findings
                if (item.severity or "").upper() == "HIGH"
            )
        },
        "findings": finding_data,
        "explanations": explanations,
        "report_note": (
            "This report presents recorded detector findings and "
            "rule-based explanations. It does not replace human review."
        )
    }


def get_audit_activity_summary(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None
) -> dict:
    """Summarise existing audit records without modifying them."""

    query = _date_filters(
        db.query(AuditLog),
        AuditLog,
        start_date,
        end_date
    )

    logs = query.all()

    action_counts = Counter(
        (log.action or "UNKNOWN").upper()
        for log in logs
    )

    entity_counts = Counter(
        (log.entity_type or "UNKNOWN")
        for log in logs
    )

    daily_counts = Counter(
        log.created_at.date().isoformat()
        for log in logs
        if log.created_at is not None
    )

    return {
        "total_events": len(logs),
        "by_action": dict(action_counts),
        "by_entity_type": dict(entity_counts),
        "daily_activity": [
            {
                "date": day,
                "count": daily_counts[day]
            }
            for day in sorted(daily_counts)
        ],
        "recent_activity": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": _parse_audit_details(log.details),
                "created_at": (
                    log.created_at.isoformat()
                    if log.created_at else None
                )
            }
            for log in sorted(
                logs,
                key=lambda item: item.id,
                reverse=True
            )[:10]
        ]
    }
