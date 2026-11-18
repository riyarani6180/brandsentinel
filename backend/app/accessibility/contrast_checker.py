
def hex_to_rgb(hex_color: str):
    """
    Convert a HEX colour into RGB values.
    """
    hex_color = hex_color.strip().lstrip("#")

    if len(hex_color) != 6:
        raise ValueError("Colour must be a 6-digit HEX value.")

    try:
        return tuple(
            int(hex_color[i:i + 2], 16)
            for i in (0, 2, 4)
        )
    except ValueError:
        raise ValueError("Invalid HEX colour.")


def get_relative_luminance(hex_color: str) -> float:
    """
    Calculate relative luminance according to WCAG.
    """
    rgb = hex_to_rgb(hex_color)

    normalized = [value / 255.0 for value in rgb]

    linear_rgb = [
        value / 12.92 if value <= 0.04045
        else ((value + 0.055) / 1.055) ** 2.4
        for value in normalized
    ]

    return (
        0.2126 * linear_rgb[0]
        + 0.7152 * linear_rgb[1]
        + 0.0722 * linear_rgb[2]
    )


def calculate_contrast_ratio(
    foreground: str,
    background: str
) -> float:
    """
    Calculate the WCAG contrast ratio between two colours.
    """
    foreground_luminance = get_relative_luminance(foreground)
    background_luminance = get_relative_luminance(background)

    lighter = max(foreground_luminance, background_luminance)
    darker = min(foreground_luminance, background_luminance)

    return round((lighter + 0.05) / (darker + 0.05), 2)


def check_contrast(
    foreground: str,
    background: str,
    is_large_text: bool = False
) -> dict:
    """
    Check whether text meets WCAG AA contrast requirements.
    """
    ratio = calculate_contrast_ratio(foreground, background)

    required_ratio = 3.0 if is_large_text else 4.5

    return {
        "foreground": foreground,
        "background": background,
        "contrast_ratio": ratio,
        "required_ratio": required_ratio,
        "passes": ratio >= required_ratio,
        "standard": "WCAG AA"
    }
