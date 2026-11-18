
from collections import Counter
from pathlib import Path

from PIL import Image


def extract_dominant_colors(
    image_path: str,
    color_count: int = 5
) -> list[str]:
    """
    Extract dominant colours from an image.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError("Image file not found.")

    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((200, 200))

        quantized = image.quantize(colors=color_count)

        palette = quantized.getpalette()
        color_counts = quantized.getcolors()

        if not color_counts or not palette:
            return []

        color_counts.sort(reverse=True)

        dominant_colors = []

        for _, color_index in color_counts:
            index = color_index * 3

            red = palette[index]
            green = palette[index + 1]
            blue = palette[index + 2]

            hex_color = "#{:02X}{:02X}{:02X}".format(
                red, green, blue
            )

            dominant_colors.append(hex_color)

        return dominant_colors


def check_brand_palette(
    image_path: str,
    approved_colors: list[str]
) -> dict:
    """
    Compare dominant image colours with approved brand colours.
    """

    if not approved_colors:
        raise ValueError("Approved brand colours are required.")

    dominant_colors = extract_dominant_colors(image_path)

    normalized_approved = {
        color.strip().upper()
        for color in approved_colors
    }

    matching_colors = [
        color for color in dominant_colors
        if color.upper() in normalized_approved
    ]

    return {
        "dominant_colors": dominant_colors,
        "approved_colors": approved_colors,
        "matching_colors": matching_colors,
        "palette_match": len(matching_colors) > 0,
        "message": (
            "Approved brand colours detected."
            if matching_colors
            else "No exact approved brand colours detected."
        )
    }
