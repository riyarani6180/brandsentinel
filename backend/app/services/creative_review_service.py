
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.brand_asset import BrandAsset

from app.accessibility.ocr_checker import extract_text_from_image
from app.accessibility.palette_checker import (
    extract_dominant_colors,
    normalize_hex_color,
    calculate_color_distance
)
from app.accessibility.alt_text_checker import check_alt_text
from app.accessibility.contrast_checker import check_contrast

from app.services.image_review_service import analyze_ocr_compliance


BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = (BACKEND_DIR / "uploads").resolve()

COLOR_DISTANCE_THRESHOLD = 45
PALETTE_MATCH_RATIO = 0.80


def resolve_reference_path(file_path: str) -> Path | None:
    """Resolve an approved reference asset safely."""

    if not file_path:
        return None

    path = Path(file_path)

    if not path.is_absolute():
        path = BACKEND_DIR / path

    path = path.resolve()

    if not path.is_relative_to(UPLOAD_ROOT):
        return None

    if not path.exists() or not path.is_file():
        return None

    return path


def get_reference_brand_colors(db: Session) -> dict:
    """Extract dominant colours from approved reference assets."""

    assets = (
        db.query(BrandAsset)
        .filter(
            BrandAsset.is_active.is_(True),
            BrandAsset.is_approved.is_(True)
        )
        .all()
    )

    approved_colors = []
    reference_assets = []
    skipped_assets = []

    for asset in assets:

        image_path = resolve_reference_path(
            asset.file_path
        )

        if image_path is None:
            skipped_assets.append(asset.id)
            continue

        try:
            colors = extract_dominant_colors(
                str(image_path),
                color_count=5
            )

            if colors:
                normalized_colors = [
                    normalize_hex_color(color)
                    for color in colors
                ]

                approved_colors.extend(normalized_colors)

                reference_assets.append({
                    "asset_id": asset.id,
                    "asset_name": asset.name,
                    "asset_type": asset.asset_type,
                    "reference_colors": normalized_colors
                })

        except Exception:
            skipped_assets.append(asset.id)

    approved_colors = list(
        dict.fromkeys(approved_colors)
    )

    return {
        "approved_colors": approved_colors,
        "reference_assets": reference_assets,
        "skipped_asset_ids": skipped_assets
    }


def compare_creative_palette(
    image_path: str,
    approved_colors: list[str]
) -> dict:
    """
    Compare every dominant creative colour against
    the approved brand palette.

    A creative passes when at least 80% of its
    dominant colours match within the distance limit.
    """

    dominant_colors = extract_dominant_colors(
        image_path,
        color_count=5
    )

    dominant_colors = [
        normalize_hex_color(color)
        for color in dominant_colors
    ]

    if not dominant_colors:
        return {
            "status": "NOT_CHECKED",
            "palette_match": None,
            "matching_percentage": 0,
            "matched_colors": [],
            "mismatched_colors": [],
            "color_matches": [],
            "message": "No dominant colours could be extracted."
        }

    if not approved_colors:
        return {
            "status": "NOT_CHECKED",
            "palette_match": None,
            "matching_percentage": 0,
            "matched_colors": [],
            "mismatched_colors": dominant_colors,
            "color_matches": [],
            "message": "No approved brand colours are available."
        }

    color_matches = []
    matched_colors = []
    mismatched_colors = []

    for image_color in dominant_colors:

        closest_color = min(
            approved_colors,
            key=lambda approved: calculate_color_distance(
                image_color,
                approved
            )
        )

        distance = calculate_color_distance(
            image_color,
            closest_color
        )

        is_match = (
            distance <= COLOR_DISTANCE_THRESHOLD
        )

        color_matches.append({
            "image_color": image_color,
            "closest_approved_color": closest_color,
            "distance": round(distance, 2),
            "is_match": is_match
        })

        if is_match:
            matched_colors.append(image_color)
        else:
            mismatched_colors.append(image_color)

    total_colors = len(dominant_colors)
    matched_count = len(matched_colors)

    matching_percentage = round(
        (matched_count / total_colors) * 100,
        2
    )

    palette_match = (
        matching_percentage
        >= PALETTE_MATCH_RATIO * 100
    )

    return {
        "status": (
            "MATCH"
            if palette_match
            else "MISMATCH"
        ),
        "palette_match": palette_match,
        "dominant_colors": dominant_colors,
        "approved_colors": approved_colors,
        "matched_colors": matched_colors,
        "mismatched_colors": mismatched_colors,
        "color_matches": color_matches,
        "matched_color_count": matched_count,
        "total_color_count": total_colors,
        "matching_percentage": matching_percentage,
        "required_matching_percentage": (
            PALETTE_MATCH_RATIO * 100
        ),
        "color_distance_threshold": COLOR_DISTANCE_THRESHOLD,
        "message": (
            "Creative palette matches the approved brand palette."
            if palette_match
            else "Creative palette does not meet the required brand colour match percentage."
        )
    }


def review_marketing_creative(
    image_path: str,
    db: Session,
    alt_text: str | None = None,
    foreground_color: str | None = None,
    background_color: str | None = None,
    is_large_text: bool = False
) -> dict:
    """
    Perform deterministic compliance and visual analysis
    of a newly submitted marketing creative.
    """

    creative_path = Path(image_path).resolve()

    if not creative_path.exists() or not creative_path.is_file():
        raise FileNotFoundError(
            "Marketing creative image not found."
        )

    # 1. Extract text using OCR.
    ocr_result = extract_text_from_image(
        str(creative_path)
    )

    extracted_text = ocr_result.get(
        "extracted_text",
        ""
    )

    # 2. Run the existing compliance engine.
    text_compliance = analyze_ocr_compliance(
        db,
        extracted_text
    )

    # 3. Retrieve approved brand reference colours.
    reference_data = get_reference_brand_colors(db)

    approved_colors = reference_data["approved_colors"]

    # 4. Compare the creative palette.
    palette_result = compare_creative_palette(
        str(creative_path),
        approved_colors
    )

    palette_result["reference_assets"] = (
        reference_data["reference_assets"]
    )

    palette_needs_review = (
        palette_result["status"] != "MATCH"
    )

    # 5. Validate alternative text.
    alt_text_result = check_alt_text(
        alt_text
    )

    # 6. Check contrast when both colours are supplied.
    contrast_result = None

    if foreground_color and background_color:

        contrast_result = check_contrast(
            foreground_color,
            background_color,
            is_large_text
        )

    # 7. Build combined review status.
    text_findings = text_compliance["total_findings"]

    accessibility_needs_review = (
        alt_text_result["status"] != "PRESENT"
        or (
            contrast_result is not None
            and not contrast_result["passes"]
        )
    )

    needs_review = (
        text_findings > 0
        or palette_needs_review
        or accessibility_needs_review
    )

    return {
        "creative_name": creative_path.name,

        "overall_status": (
            "REQUIRES_REVIEW"
            if needs_review
            else "PASSED"
        ),

        "text_compliance": text_compliance,

        "visual_compliance": {
            "palette": palette_result,
            "reference_assets": (
                reference_data["reference_assets"]
            ),
            "skipped_reference_asset_ids": (
                reference_data["skipped_asset_ids"]
            )
        },

        "accessibility": {
            "alt_text": alt_text_result,
            "contrast": contrast_result
        },

        "summary": {
            "text_findings": text_findings,
            "palette_status": palette_result["status"],
            "palette_matching_percentage": (
                palette_result.get("matching_percentage")
            ),
            "alt_text_status": alt_text_result["status"],
            "contrast_checked": contrast_result is not None,
            "requires_human_review": needs_review
        },

        "message": "Marketing creative review completed."
    }
