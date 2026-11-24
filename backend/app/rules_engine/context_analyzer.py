
"""
BrandSentinel - Context Analyzer

Examines surrounding sentences to identify whether
a potentially risky claim has nearby qualifying
or supporting language.

This is a rule-based context signal, not proof
of compliance or factual accuracy.
"""

import re


QUALIFYING_PATTERNS = [
    r"\b(may|might|can|could|potentially|typically|generally)\b",
    r"\b(under certain conditions|in some cases|for some users)\b",
    r"\b(results may vary|individual results may vary)\b",
    r"\b(subject to|depending on|when used as directed)\b",
]

EVIDENCE_PATTERNS = [
    r"\b(clinical study|clinical trial|laboratory test)\b",
    r"\b(independent testing|tested by|certified by)\b",
    r"\b(research shows|study found|according to)\b",
    r"\b(test results|published research|official report)\b",
]

ABSOLUTE_PATTERNS = [
    r"(?<!\w)100%(?!\w)",
    r"\b(completely|totally|always|never|guaranteed)\b",
    r"\b(zero risk|no side effects|instant results)\b",
]


def split_sentences(text: str) -> list[str]:
    """Split content into sentences."""
    if not text or not text.strip():
        return []

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def contains_pattern(text: str, patterns: list[str]) -> bool:
    """Check whether any supplied pattern occurs in text."""
    return any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in patterns
    )


def analyze_sentence_context(
    sentences: list[str],
    index: int,
    context_window: int = 1
) -> dict:
    """
    Examine the current sentence and nearby sentences.

    context_window=1 checks one sentence before and
    after the current sentence.
    """

    if not sentences or index < 0 or index >= len(sentences):
        raise ValueError("Invalid sentence index")

    start = max(0, index - context_window)
    end = min(len(sentences), index + context_window + 1)

    surrounding_text = " ".join(sentences[start:end])
    current_sentence = sentences[index]

    has_qualifying_language = contains_pattern(
        surrounding_text, QUALIFYING_PATTERNS
    )

    has_evidence_reference = contains_pattern(
        surrounding_text, EVIDENCE_PATTERNS
    )

    has_absolute_language = contains_pattern(
        current_sentence, ABSOLUTE_PATTERNS
    )

    if has_qualifying_language:
        context_status = "QUALIFIED_LANGUAGE"
    elif has_evidence_reference:
        context_status = "EVIDENCE_REFERENCE_PRESENT"
    elif has_absolute_language:
        context_status = "ABSOLUTE_LANGUAGE"
    else:
        context_status = "NEEDS_CONTEXT_REVIEW"

    return {
        "sentence": current_sentence,
        "surrounding_context": surrounding_text,
        "has_qualifying_language": has_qualifying_language,
        "has_evidence_reference": has_evidence_reference,
        "has_absolute_language": has_absolute_language,
        "context_status": context_status,
        "requires_human_review": (
            has_absolute_language
            or not has_qualifying_language
        )
    }


def analyze_submission_context(
    content: str,
    context_window: int = 1
) -> list[dict]:
    """Analyze the context of every sentence in a submission."""

    sentences = split_sentences(content)

    return [
        analyze_sentence_context(
            sentences,
            index,
            context_window
        )
        for index in range(len(sentences))
    ]
