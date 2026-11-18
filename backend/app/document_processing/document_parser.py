
from pathlib import Path

import fitz
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF document.
    """

    extracted_text = []

    with fitz.open(file_path) as pdf:
        for page in pdf:
            extracted_text.append(page.get_text())

    return "\n".join(extracted_text).strip()


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a DOCX document.
    """

    document = Document(file_path)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs).strip()


def extract_document_text(file_path: str) -> str:
    """
    Extract text based on the document extension.
    """

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension == ".docx":
        return extract_text_from_docx(file_path)

    else:
        raise ValueError(
            "Unsupported document format. Use PDF or DOCX."
        )
