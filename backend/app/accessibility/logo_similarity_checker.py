
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


SIMILARITY_THRESHOLD = 85.0
HASH_SIZE = 64


def prepare_image(image_path: str) -> np.ndarray:
    """
    Normalize an image while preserving its aspect ratio.

    Transparent areas are composited onto a white background.
    """

    path = Path(image_path)

    if not path.exists() or not path.is_file():
        raise FileNotFoundError("Logo image not found.")

    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGBA")

        background = Image.new(
            "RGBA",
            image.size,
            (255, 255, 255, 255)
        )

        image = Image.alpha_composite(background, image)
        image = image.convert("L")

        image.thumbnail(
            (HASH_SIZE, HASH_SIZE),
            Image.Resampling.LANCZOS
        )

        # Place the image on a fixed white canvas.
        canvas = Image.new(
            "L",
            (HASH_SIZE, HASH_SIZE),
            255
        )

        x = (HASH_SIZE - image.width) // 2
        y = (HASH_SIZE - image.height) // 2

        canvas.paste(image, (x, y))

        return np.asarray(
            canvas,
            dtype=np.float32
        )


def compare_logo_images(
    submitted_logo_path: str,
    approved_logo_path: str
) -> dict:
    """
    Compare actual normalized image pixels.

    Similarity is based on normalized mean absolute
    grayscale pixel difference.
    """

    submitted = prepare_image(submitted_logo_path)
    approved = prepare_image(approved_logo_path)

    mean_difference = float(
        np.mean(np.abs(submitted - approved))
    )

    similarity = max(
        0.0,
        1.0 - (mean_difference / 255.0)
    )

    score = round(similarity * 100, 2)

    if score >= SIMILARITY_THRESHOLD:
        status = "MATCH"
        message = (
            "Submitted image is sufficiently similar "
            "to the approved logo reference."
        )
    else:
        status = "MISMATCH"
        message = (
            "Submitted image differs from the approved "
            "logo reference."
        )

    return {
        "status": status,
        "similarity_score": score,
        "required_similarity_score": SIMILARITY_THRESHOLD,
        "mean_pixel_difference": round(mean_difference, 2),
        "message": message
    }


def verify_logo_identity(
    submitted_logo_path: str,
    approved_logo_paths: list[dict]
) -> dict:
    """
    Compare a submitted logo against all approved
    logo references and return the best comparison.
    """

    if not approved_logo_paths:
        return {
            "status": "INCONCLUSIVE",
            "similarity_score": None,
            "reference_asset": None,
            "comparisons": [],
            "message": "No approved logo reference is available."
        }

    comparisons = []
    skipped_references = []

    for reference in approved_logo_paths:

        try:
            result = compare_logo_images(
                submitted_logo_path,
                reference["file_path"]
            )

            result["asset_id"] = reference.get("asset_id")
            result["asset_name"] = reference.get("asset_name")

            comparisons.append(result)

        except (OSError, ValueError, KeyError) as error:
            skipped_references.append({
                "asset_id": reference.get("asset_id"),
                "reason": str(error)
            })

    if not comparisons:
        return {
            "status": "INCONCLUSIVE",
            "similarity_score": None,
            "reference_asset": None,
            "comparisons": [],
            "skipped_references": skipped_references,
            "message": "No valid approved logo references could be compared."
        }

    best_match = max(
        comparisons,
        key=lambda item: item["similarity_score"]
    )

    return {
        "status": best_match["status"],
        "similarity_score": best_match["similarity_score"],
        "reference_asset": {
            "asset_id": best_match["asset_id"],
            "asset_name": best_match["asset_name"]
        },
        "comparisons": comparisons,
        "skipped_references": skipped_references,
        "message": best_match["message"]
    }
