
import re
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.brand_asset import BrandAsset
from app.models.guideline import Guideline
from app.models.approved_fact import ApprovedFact

from app.accessibility.ocr_checker import extract_text_from_image
from app.accessibility.palette_checker import check_brand_palette
from app.accessibility.alt_text_checker import check_alt_text
from app.accessibility.contrast_checker import check_contrast

from app.rules_engine.guideline_parser import extract_brand_rules
from app.rules_engine.text_rules import analyze_banned_terms
from app.rules_engine.terminology_rules import analyze_preferred_terms
from app.rules_engine.context_analyzer import analyze_submission_context

from app.claims_ledger.claims_verifier import verify_claims

from app.ai_engine.misleading_claim_detector import detect_misleading_claims
from app.ai_engine.confidence_score import score_finding


# Patterns indicating potentially verifiable product or performance claims.
FACTUAL_CLAIM_PATTERN = re.compile(
    r"\b(?:"
    r"up to|at least|more than|less than|"
    r"lasts?|provides?|delivers?|offers?|"
    r"supports?|contains?|includes?|"
    r"weighs?|measures?|reduces?|"
    r"increases?|improves?|prevents?|"
    r"protects?|compatible with|"
    r"battery life|battery backup"
    r")\b"
    r"|\b\d+(?:\.\d+)?\s*(?:%|hours?|hrs?|"
    r"minutes?|mins?|days?|years?|"
    r"GB|TB|MB|mAh|kg|grams?|watts?|W)\b",
    re.IGNORECASE
)


def contains_factual_claim(text: str) -> bool:
    """
    Identify text containing a potentially verifiable
    product or performance claim.
    """

    if not text or not text.strip():
        return False

    return bool(
        FACTUAL_CLAIM_PATTERN.search(text)
    )


def analyze_ocr_compliance(db: Session, extracted_text: str) -> dict:
    """
    Apply existing BrandSentinel text compliance rules
    to text extracted from an image.
    """

    if not extracted_text or not extracted_text.strip():
        return {
            "status": "NO_TEXT_DETECTED",
            "total_findings": 0,
            "findings": [],
            "context_analysis": [],
            "message": "No readable text was available for compliance analysis."
        }

    all_findings = []

    guidelines = (
        db.query(Guideline)
        .filter(Guideline.is_active.is_(True))
        .all()
    )

    # 1. Check active brand guidelines.
    for guideline in guidelines:

        rules = extract_brand_rules(guideline.content)

        all_findings.extend(
            analyze_banned_terms(
                extracted_text,
                rules["banned_terms"]
            )
        )

        all_findings.extend(
            analyze_preferred_terms(
                extracted_text,
                rules["preferred_terms"]
            )
        )

    # 2. Load active and currently valid approved facts.
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
            "source_reference": fact.source_reference
        }
        for fact in approved_facts
    ]

    # 3. Verify only potentially factual claims.
    # Ordinary headings and brand names should not
    # automatically generate unverified-claim warnings.
    if contains_factual_claim(extracted_text):

        claim_findings = verify_claims(
            extracted_text,
            fact_data
        )

        all_findings.extend(claim_findings)

    # 4. Detect potentially misleading promotional wording.
    all_findings.extend(
        detect_misleading_claims(extracted_text)
    )

    # 5. Analyse context.
    context_results = analyze_submission_context(
        extracted_text,
        context_window=1
    )

    # 6. Score and prepare findings.
    findings = []

    for finding in all_findings:

        scored = score_finding(finding)

        finding_type = str(
            scored.get("finding_type", "")
        ).upper()

        status_mapping = {
            "BANNED_TERM": "VIOLATION_DETECTED",
            "PREFERRED_TERMINOLOGY": "TERMINOLOGY_REVIEW",
            "CLAIM_VERIFICATION": "UNVERIFIED",
            "NUMERICAL_CONTRADICTION": "CONTRADICTED",
            "MISLEADING_CLAIM": "REQUIRES_REVIEW"
        }

        scored["verification_status"] = (
            scored.get("verification_status")
            or status_mapping.get(
                finding_type,
                "REQUIRES_REVIEW"
            )
        )

        scored["source_type"] = "IMAGE_OCR"
        scored["requires_human_review"] = (
            scored.get("confidence", 0) < 0.70
            or finding_type in {
                "CLAIM_VERIFICATION",
                "MISLEADING_CLAIM"
            }
        )

        findings.append(scored)

    # 7. Determine overall image-text status.
    if not findings:
        status = "PASSED"
    else:
        status = "REQUIRES_REVIEW"

    return {
        "status": status,
        "total_findings": len(findings),
        "findings": findings,
        "context_analysis": context_results,
        "message": (
            "Image text compliance analysis completed."
        )
    }


def analyze_brand_image(
    asset: BrandAsset,
    db: Session,
    approved_colors: list[str],
    alt_text: str | None = None,
    foreground_color: str | None = None,
    background_color: str | None = None,
    is_large_text: bool = False
) -> dict:
    """
    Analyse an approved brand image for accessibility,
    visual identity, and text compliance.
    """

    if not asset.is_active or not asset.is_approved:
        raise ValueError(
            "Only active, approved brand assets can be analyzed."
        )

    image_path = Path(asset.file_path)

    if not image_path.exists():
        raise FileNotFoundError(
            "Brand asset image not found."
        )

    # 1. Extract text using OCR.
    ocr_result = extract_text_from_image(
        str(image_path)
    )

    # 2. Run extracted text through compliance rules.
    text_compliance = analyze_ocr_compliance(
        db,
        ocr_result.get("extracted_text", "")
    )

    # 3. Check approved brand palette.
    palette_result = check_brand_palette(
        str(image_path),
        approved_colors
    )

    # 4. Check alternative text.
    alt_text_result = check_alt_text(
        alt_text
    )

    # 5. Check text contrast when colours are provided.
    contrast_result = None

    if foreground_color and background_color:
        contrast_result = check_contrast(
            foreground_color,
            background_color,
            is_large_text
        )

    return {
        "asset_id": asset.id,
        "asset_name": asset.name,
        "ocr": ocr_result,
        "text_compliance": text_compliance,
        "palette": palette_result,
        "alt_text": alt_text_result,
        "contrast": contrast_result
    }
