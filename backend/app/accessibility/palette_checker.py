
from pathlib import Path
from collections import Counter
from math import sqrt

from PIL import Image


# Maximum RGB distance allowed for a colour match.
# RGB distance ranges from 0 to approximately 441.67.
COLOR_DISTANCE_THRESHOLD = 45


def normalize_hex_color(color: str) -> str:
    """Validate and normalize a HEX colour."""

    if not isinstance(color, str):
        raise ValueError("Brand colours must be HEX strings.")

    color = color.strip().upper()

    if not color.startswith("#"):
        color = "#" + color

    if (
        len(color) != 7
        or any(character not in "0123456789ABCDEF" for character in color[1:])
    ):
        raise ValueError(f"Invalid HEX colour: {color}")

    return color


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Convert HEX colour to RGB."""

    color = normalize_hex_color(color)

    return (
        int(color[1:3], 16),
        int(color[3:5], 16),
        int(color[5:7], 16)
    )


def calculate_color_distance(
    color1: str,
    color2: str
) -> float:
    """Calculate Euclidean distance between two RGB colours."""

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    return sqrt(
        sum(
            (component1 - component2) ** 2
            for component1, component2 in zip(rgb1, rgb2)
        )
    )


def extract_dominant_colors(
    image_path: str,
    color_count: int = 5
) -> list[str]:
    """Extract dominant colours from an image."""

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError("Image file not found.")

    if color_count < 1:
        raise ValueError("Color count must be at least 1.")

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
    approved_colors: list[str],
    distance_threshold: float = COLOR_DISTANCE_THRESHOLD
) -> dict:
    """
    Compare dominant image colours with approved brand colours.

    A colour is considered a match when its RGB distance
    from an approved colour is within the configured threshold.
    """

    if not approved_colors:
        raise ValueError("Approved brand colours are required.")

    if distance_threshold < 0:
        raise ValueError("Colour distance threshold cannot be negative.")

    normalized_approved = list(dict.fromkeys(
        normalize_hex_color(color)
        for color in approved_colors
    ))

    dominant_colors = extract_dominant_colors(image_path)

    matching_colors = []
    color_matches = []

    for dominant_color in dominant_colors:

        closest_match = None
        minimum_distance = float("inf")

        for approved_color in normalized_approved:

            distance = calculate_color_distance(
                dominant_color,
                approved_color
            )

            if distance < minimum_distance:
                minimum_distance = distance
                closest_match = approved_color

        is_match = minimum_distance <= distance_threshold

        if is_match:
            matching_colors.append(dominant_color)

        color_matches.append({
            "image_color": dominant_color,
            "closest_approved_color": closest_match,
            "distance": round(minimum_distance, 2),
            "is_match": is_match
        })

    palette_match = len(matching_colors) > 0

    return {
        "dominant_colors": dominant_colors,
        "approved_colors": normalized_approved,
        "matching_colors": matching_colors,
        "color_matches": color_matches,
        "distance_threshold": distance_threshold,
        "palette_match": palette_match,
        "message": (
            "Approved brand colours or sufficiently similar shades detected."
            if palette_match
            else "No approved or sufficiently similar brand colours detected."
        )
    }
