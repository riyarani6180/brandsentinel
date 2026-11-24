
import re
from typing import Any


# Recognized measurement units.
# The final lookahead also supports percentage values such as 100%.
UNIT_PATTERN = re.compile(
    r"(?<![\w.])"
    r"(\d+(?:\.\d+)?)\s*"
    r"(hours?|hrs?|days?|years?|months?|"
    r"gb|tb|mb|kg|grams?|g|ml|"
    r"litres?|liters?|mah|watts?|w|hz|%)"
    r"(?![a-z])",
    flags=re.IGNORECASE,
)


UNIT_ALIASES = {
    "hour": "hours",
    "hours": "hours",
    "hr": "hours",
    "hrs": "hours",
    "day": "days",
    "days": "days",
    "year": "years",
    "years": "years",
    "month": "months",
    "months": "months",
    "litre": "litres",
    "litres": "litres",
    "liter": "litres",
    "liters": "litres",
    "gram": "grams",
    "grams": "grams",
    "g": "grams",
    "watt": "watts",
    "watts": "watts",
    "w": "watts",
    "%": "%",
}


def normalize_unit(unit: str) -> str:
    """Normalize equivalent measurement unit spellings."""

    normalized = unit.strip().lower()

    return UNIT_ALIASES.get(normalized, normalized)


def extract_measurements(text: str) -> list[dict[str, Any]]:
    """Extract numerical measurements and their normalized units."""

    if not text:
        return []

    measurements = []

    for match in UNIT_PATTERN.finditer(text):

        value = float(match.group(1))
        unit = normalize_unit(match.group(2))

        measurements.append({
            "value": value,
            "unit": unit,
        })

    return measurements


def detect_contradictions(
    semantic_matches: list[dict[str, Any]],
    similarity_threshold: float = 0.70,
) -> list[dict[str, Any]]:
    """
    Detect numerical contradictions between submitted claims
    and semantically related approved facts.

    A contradiction is reported only when:
    - Semantic similarity meets the threshold.
    - Both texts contain recognized measurements.
    - At least one equivalent unit has a different value.
    """

    findings = []
    seen_pairs = set()

    for result in semantic_matches:

        claim = str(result.get("claim") or "").strip()

        if not claim:
            continue

        submitted_measurements = extract_measurements(claim)

        if not submitted_measurements:
            continue

        for fact in result.get("matched_facts", []):

            approved_text = str(
                fact.get("fact_content") or ""
            ).strip()

            if not approved_text:
                continue

            try:
                similarity = float(fact.get("similarity", 0))
            except (TypeError, ValueError):
                continue

            if not 0.0 <= similarity <= 1.0:
                continue

            if similarity < similarity_threshold:
                continue

            approved_measurements = extract_measurements(
                approved_text
            )

            if not approved_measurements:
                continue

            # Find conflicting values using equivalent units.
            conflicting_measurement = None

            for submitted in submitted_measurements:

                for approved in approved_measurements:

                    if submitted["unit"] != approved["unit"]:
                        continue

                    if submitted["value"] != approved["value"]:

                        conflicting_measurement = (
                            submitted,
                            approved,
                        )
                        break

                if conflicting_measurement:
                    break

            if not conflicting_measurement:
                continue

            submitted, approved = conflicting_measurement

            pair_key = (
                claim.casefold(),
                approved_text.casefold(),
                submitted["unit"],
            )

            if pair_key in seen_pairs:
                continue

            seen_pairs.add(pair_key)

            findings.append({
                "finding_type": "NUMERICAL_CONTRADICTION",
                "severity": "HIGH",
                "description": (
                    "A submitted numerical claim conflicts "
                    "with a semantically related approved fact."
                ),
                "evidence": (
                    f"Submitted claim: {claim}\n"
                    f"Approved fact: {approved_text}"
                ),
                "source_reference": fact.get("source_reference"),
                "suggested_fix": (
                    f"Verify the measurement and use the approved "
                    f"value of {approved['value']:g} "
                    f"{approved['unit']}."
                ),
                "confidence": round(
                    min(
                        0.99,
                        0.80 + (similarity - 0.70) * 0.5,
                    ),
                    2,
                ),
                "verification_status": "CONTRADICTED",
            })

    return findings
