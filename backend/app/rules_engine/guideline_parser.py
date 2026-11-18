
import re


def extract_brand_rules(guideline_text: str) -> dict:
    """
    Extract structured brand rules from guideline text.

    Supported formats:

    BANNED: guaranteed
    PREFERRED: cheap -> affordable
    """

    rules = {
        "banned_terms": [],
        "preferred_terms": []
    }

    if not guideline_text:
        return rules

    lines = guideline_text.splitlines()

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()

        # Extract banned terms.
        banned_match = re.match(
            r"^BANNED:\s*(.+)$",
            line,
            flags=re.IGNORECASE
        )

        if banned_match:
            term = banned_match.group(1).strip()

            if term:
                rules["banned_terms"].append({
                    "term": term,
                    "source_reference": (
                        f"Brand Guidelines - Line {line_number}"
                    ),
                    "suggested_fix": (
                        f"Remove or replace the banned term '{term}'."
                    ),
                    "severity": "HIGH"
                })

        # Extract preferred terminology.
        preferred_match = re.match(
            r"^PREFERRED:\s*(.+?)\s*->\s*(.+)$",
            line,
            flags=re.IGNORECASE
        )

        if preferred_match:
            non_preferred = preferred_match.group(1).strip()
            preferred = preferred_match.group(2).strip()

            if non_preferred and preferred:
                rules["preferred_terms"].append({
                    "non_preferred_term": non_preferred,
                    "preferred_term": preferred,
                    "source_reference": (
                        f"Brand Guidelines - Line {line_number}"
                    ),
                    "severity": "MEDIUM"
                })

    return rules
