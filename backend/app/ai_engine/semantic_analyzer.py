from functools import lru_cache
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_semantic_model():
    """
    Load the semantic model once and reuse it.
    The model is downloaded on first use.
    """
    return SentenceTransformer(DEFAULT_MODEL)


def extract_sentences(text: str) -> list[str]:
    """
    Split submitted content into individual sentences.
    """
    if not text or not text.strip():
        return []

    import re

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def compare_claims_with_approved_facts(
    claims: list[str],
    approved_facts: list[dict[str, Any]],
    top_k: int = 3
) -> list[dict[str, Any]]:
    """
    Find the most semantically relevant approved facts
    for every submitted claim.

    Expected approved fact format:

    {
        "fact_content": "Product contains 2% salicylic acid",
        "source_reference": "Official product specification"
    }
    """

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

    model = get_semantic_model()

    # Convert claims and approved facts into embeddings.
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

    # Cosine similarity between normalized embeddings.
    similarity_matrix = np.matmul(
        claim_embeddings,
        fact_embeddings.T
    )

    results = []

    for claim_index, claim in enumerate(clean_claims):

        similarities = similarity_matrix[claim_index]

        ranked_indices = np.argsort(similarities)[::-1]

        matches = []

        for fact_index in ranked_indices[:max(1, top_k)]:

            similarity = float(similarities[fact_index])

            fact = valid_facts[int(fact_index)]

            matches.append({
                "fact_content": fact_texts[int(fact_index)],
                "source_reference": fact.get(
                    "source_reference"
                ),
                "similarity": round(
                    max(0.0, min(1.0, similarity)),
                    4
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
    """
    Main entry point for semantic analysis.

    Extracts sentences and compares them with
    approved brand facts.
    """

    claims = extract_sentences(submission_text)

    return compare_claims_with_approved_facts(
        claims=claims,
        approved_facts=approved_facts,
        top_k=top_k
    )
