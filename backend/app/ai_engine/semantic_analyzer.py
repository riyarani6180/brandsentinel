
import os
import re
from functools import lru_cache
from typing import Any

import numpy as np


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

LIGHTWEIGHT_MODE = (
    os.getenv("LIGHTWEIGHT_SEMANTIC_MODE", "false").lower()
    == "true"
)


@lru_cache(maxsize=1)
def get_semantic_model():
    """
    Load the Sentence Transformer only when needed.
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(DEFAULT_MODEL)


def extract_sentences(text: str) -> list[str]:
    if not text or not text.strip():
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def calculate_keyword_similarity(text1: str, text2: str) -> float:
    """
    Lightweight token-overlap similarity.
    Does not load PyTorch or a machine-learning model.
    """
    words1 = set(re.findall(r"\b\w+\b", text1.lower()))
    words2 = set(re.findall(r"\b\w+\b", text2.lower()))

    if not words1 or not words2:
        return 0.0

    return len(words1 & words2) / len(words1 | words2)


def compare_claims_with_approved_facts(
    claims: list[str],
    approved_facts: list[dict[str, Any]],
    top_k: int = 3
) -> list[dict[str, Any]]:

    if not claims or not approved_facts:
        return []

    valid_facts = [
        fact for fact in approved_facts
        if isinstance(fact, dict)
        and fact.get("fact_content")
        and str(fact["fact_content"]).strip()
    ]

    if not valid_facts:
        return []

    clean_claims = [
        str(claim).strip()
        for claim in claims
        if claim and str(claim).strip()
    ]

    if not clean_claims:
        return []

    fact_texts = [
        str(fact["fact_content"]).strip()
        for fact in valid_facts
    ]

    results = []

    if LIGHTWEIGHT_MODE:
        # Memory-friendly matching for Render Free.
        for claim in clean_claims:
            matches = []

            for index, fact_text in enumerate(fact_texts):
                similarity = calculate_keyword_similarity(
                    claim, fact_text
                )

                matches.append({
                    "fact_content": fact_text,
                    "source_reference": valid_facts[index].get(
                        "source_reference"
                    ),
                    "similarity": round(similarity, 4)
                })

            matches.sort(
                key=lambda item: item["similarity"],
                reverse=True
            )

            results.append({
                "claim": claim,
                "matched_facts": matches[:max(1, top_k)]
            })

        return results

    # Full semantic model for local development.
    model = get_semantic_model()

    claim_embeddings = model.encode(
        clean_claims,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    fact_embeddings = model.encode(
        fact_texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    similarity_matrix = np.matmul(
        claim_embeddings,
        fact_embeddings.T
    )

    for claim_index, claim in enumerate(clean_claims):
        similarities = similarity_matrix[claim_index]
        ranked_indices = np.argsort(similarities)[::-1]

        matches = []

        for fact_index in ranked_indices[:max(1, top_k)]:
            similarity = float(similarities[fact_index])
            fact = valid_facts[int(fact_index)]

            matches.append({
                "fact_content": fact_texts[int(fact_index)],
                "source_reference": fact.get("source_reference"),
                "similarity": round(
                    max(0.0, min(1.0, similarity)), 4
                )
            })

        results.append({
            "claim": claim,
            "matched_facts": matches
        })

    return results


def analyze_submission_semantics(
    submission_text: str,
    approved_facts: list[dict[str, Any]],
    top_k: int = 3
) -> list[dict[str, Any]]:

    claims = extract_sentences(submission_text)

    return compare_claims_with_approved_facts(
        claims=claims,
        approved_facts=approved_facts,
        top_k=top_k
    )
