
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.security.dependencies import get_current_user
from app.document_processing.document_parser import extract_document_text


router = APIRouter(
    prefix="/documents",
    tags=["Document Processing"]
)

BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "uploads"

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/extract")
async def upload_and_extract_document(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are supported."
        )

    file_content = await file.read(MAX_FILE_SIZE + 1)

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must not exceed 10 MB."
        )

    if extension == ".pdf" and not file_content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid PDF file."
        )

    if extension == ".docx" and not file_content.startswith(b"PK"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid DOCX file."
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    saved_filename = f"{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        file_path.write_bytes(file_content)

        extracted_text = extract_document_text(str(file_path))

        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text found in the document."
            )

        return {
            "filename": file.filename,
            "extracted_text": extracted_text,
            "message": "Document text extracted successfully."
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not process this document."
        )

    finally:
        if file_path.exists():
            file_path.unlink()
