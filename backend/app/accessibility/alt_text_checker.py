
def check_alt_text(alt_text: str | None) -> dict:
    """
    Check whether an image has meaningful alternative text.
    """

    if alt_text is None or not alt_text.strip():
        return {
            "has_alt_text": False,
            "status": "MISSING",
            "message": "Image is missing alternative text.",
            "suggestion": "Add a meaningful description of the image."
        }

    normalized_text = alt_text.strip().lower()

    generic_values = {
        "image",
        "picture",
        "photo",
        "graphic",
        "img",
        "image1",
        "picture1"
    }

    if normalized_text in generic_values:
        return {
            "has_alt_text": False,
            "status": "GENERIC",
            "message": "Image alternative text is too generic.",
            "suggestion": "Describe the actual content or purpose of the image."
        }

    return {
        "has_alt_text": True,
        "status": "PRESENT",
        "message": "Image alternative text is present.",
        "suggestion": None
    }
