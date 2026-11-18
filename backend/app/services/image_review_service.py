
from pathlib import Path

from app.models.brand_asset import BrandAsset

from app.accessibility.ocr_checker import extract_text_from_image
from app.accessibility.palette_checker import check_brand_palette
from app.accessibility.alt_text_checker import check_alt_text
from app.accessibility.contrast_checker import check_contrast


def analyze_brand_image(
    asset: BrandAsset,
    approved_colors: list[str],
    alt_text: str | None = None,
    foreground_color: str | None = None,
    background_color: str | None = None,
    is_large_text: bool = False
) -> dict:
    """
    Run accessibility checks on an approved brand image.
    """

    if not asset.is_active or not asset.is_approved:
        raise ValueError(
            "Only active, approved brand assets can be analyzed."
        )

    image_path = Path(asset.file_path)

    if not image_path.exists():
        raise FileNotFoundError("Brand asset image not found.")

    # Extract text embedded in the image.
    ocr_result = extract_text_from_image(str(image_path))

    # Compare image colours with the approved brand palette.
    palette_result = check_brand_palette(
        str(image_path),
        approved_colors
    )

    # Check whether alternative text is meaningful.
    alt_text_result = check_alt_text(alt_text)

    # Run contrast analysis when both colours are supplied.
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
        "palette": palette_result,
        "alt_text": alt_text_result,
        "contrast": contrast_result
    }
