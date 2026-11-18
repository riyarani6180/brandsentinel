
from pathlib import Path

import pytesseract
from PIL import Image


# Configure the installed Tesseract executable.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_image(image_path: str) -> dict:
    """
    Extract text embedded inside an image using OCR.
    """

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError("Image file not found.")

    try:
        with Image.open(path) as image:
            extracted_text = pytesseract.image_to_string(
                image
            ).strip()

        return {
            "image": path.name,
            "extracted_text": extracted_text,
            "text_detected": bool(extracted_text),
            "message": (
                "Text extracted successfully."
                if extracted_text
                else "No readable text detected in the image."
            )
        }

    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR executable could not be found."
        )

    except Exception as error:
        raise ValueError(
            f"Could not process image: {error}"
        )
