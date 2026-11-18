
from pathlib import Path
from uuid import uuid4
import mimetypes

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.connection import get_db
from app.models.brand_asset import BrandAsset
from app.models.user import User

from app.schemas.brand_asset import (
    BrandAssetCreate,
    BrandAssetUpdate,
    BrandAssetResponse
)

from app.security.dependencies import get_current_user
from app.security.permissions import require_user_permission

from app.services.image_review_service import analyze_brand_image


router = APIRouter(
    prefix="/brand-assets",
    tags=["Brand Assets"]
)


# ==========================================
# IMAGE ANALYSIS REQUEST
# ==========================================

class ImageAnalysisRequest(BaseModel):
    approved_colors: list[str] = Field(..., min_length=1)
    alt_text: str | None = None
    foreground_color: str | None = None
    background_color: str | None = None
    is_large_text: bool = False


# ==========================================
# UPLOAD CONFIGURATION
# ==========================================

BACKEND_DIR = Path(__file__).resolve().parents[2]

UPLOAD_ROOT = (BACKEND_DIR / "uploads").resolve()

UPLOAD_DIR = UPLOAD_ROOT / "brand_assets"

ALLOWED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}

MAX_FILE_SIZE = 10 * 1024 * 1024


# ==========================================
# IMAGE VALIDATION
# ==========================================

def validate_image(content: bytes, extension: str):

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded image is empty."
        )

    valid = False

    if extension == ".png":
        valid = content.startswith(
            b"\x89PNG\r\n\x1a\n"
        )

    elif extension in {".jpg", ".jpeg"}:
        valid = content.startswith(
            b"\xff\xd8\xff"
        )

    elif extension == ".webp":
        valid = (
            len(content) >= 12
            and content.startswith(b"RIFF")
            and content[8:12] == b"WEBP"
        )

    if not valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. Upload a valid PNG, JPG or WEBP image."
        )


# ==========================================
# RESOLVE IMAGE PATH
# ==========================================

def resolve_asset_image_path(file_path: str) -> Path:

    if not file_path:
        raise HTTPException(
            status_code=404,
            detail="Image path is missing."
        )

    image_path = Path(file_path)

    # Support old relative paths and new absolute paths.
    if not image_path.is_absolute():
        image_path = BACKEND_DIR / image_path

    image_path = image_path.resolve()

    # Prevent access to files outside the uploads directory.
    if not image_path.is_relative_to(UPLOAD_ROOT):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file location."
        )

    if not image_path.exists() or not image_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Image file not found. Please upload the image again."
        )

    return image_path


# ==========================================
# CREATE BRAND ASSET USING EXISTING FILE
# ==========================================

@router.post(
    "/",
    response_model=BrandAssetResponse,
    status_code=status.HTTP_201_CREATED
)
def create_brand_asset(
    asset_data: BrandAssetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("MANAGE_BRAND_ASSETS")
    )
):

    new_asset = BrandAsset(
        name=asset_data.name,
        asset_type=asset_data.asset_type,
        file_path=asset_data.file_path,
        description=asset_data.description,
        is_approved=False,
        is_active=True
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset


# ==========================================
# UPLOAD NEW BRAND ASSET
# ==========================================

@router.post(
    "/upload",
    response_model=BrandAssetResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_brand_asset(
    name: str = Form(...),
    asset_type: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("MANAGE_BRAND_ASSETS")
    )
):

    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PNG, JPG, JPEG and WEBP images are supported."
        )

    if len(name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Asset name must contain at least 2 characters."
        )

    if len(asset_type.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Asset type must contain at least 2 characters."
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    try:

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image size must not exceed 10 MB."
            )

        validate_image(content, extension)

        UPLOAD_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        saved_filename = f"{uuid4().hex}{extension}"

        saved_path = (UPLOAD_DIR / saved_filename).resolve()

        if not saved_path.is_relative_to(UPLOAD_ROOT):
            raise HTTPException(
                status_code=400,
                detail="Invalid upload location."
            )

        saved_path.write_bytes(content)

        new_asset = BrandAsset(
            name=name.strip(),
            asset_type=asset_type.strip(),
            file_path=str(saved_path),
            description=description.strip() or None,
            is_approved=False,
            is_active=True
        )

        db.add(new_asset)
        db.commit()
        db.refresh(new_asset)

        return new_asset

    except HTTPException:
        db.rollback()

        if "saved_path" in locals() and saved_path.exists():
            saved_path.unlink()

        raise

    except Exception:
        db.rollback()

        if "saved_path" in locals() and saved_path.exists():
            saved_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Could not save the brand asset."
        )

    finally:
        await file.close()


# ==========================================
# GET ALL BRAND ASSETS
# ==========================================

@router.get(
    "/",
    response_model=list[BrandAssetResponse]
)
def get_brand_assets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    query = db.query(BrandAsset).filter(
        BrandAsset.is_active.is_(True)
    )

    if current_user.role != "BRAND_ADMIN":
        query = query.filter(
            BrandAsset.is_approved.is_(True)
        )

    return query.order_by(
        BrandAsset.id.desc()
    ).all()


# ==========================================
# GET BRAND ASSET IMAGE
# ==========================================

@router.get("/{asset_id}/image")
def get_brand_asset_image(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    asset = db.query(BrandAsset).filter(
        BrandAsset.id == asset_id,
        BrandAsset.is_active.is_(True)
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Brand asset not found."
        )

    if (
        not asset.is_approved
        and current_user.role != "BRAND_ADMIN"
    ):
        raise HTTPException(
            status_code=403,
            detail="This asset is not approved."
        )

    image_path = resolve_asset_image_path(
        asset.file_path
    )

    media_type, _ = mimetypes.guess_type(
        str(image_path)
    )

    return FileResponse(
        path=str(image_path),
        media_type=media_type or "application/octet-stream",
        filename=image_path.name
    )


# ==========================================
# GET INDIVIDUAL BRAND ASSET
# ==========================================

@router.get(
    "/{asset_id}",
    response_model=BrandAssetResponse
)
def get_brand_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    asset = db.query(BrandAsset).filter(
        BrandAsset.id == asset_id,
        BrandAsset.is_active.is_(True)
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Brand asset not found."
        )

    if (
        not asset.is_approved
        and current_user.role != "BRAND_ADMIN"
    ):
        raise HTTPException(
            status_code=403,
            detail="This asset is not approved."
        )

    return asset


# ==========================================
# UPDATE BRAND ASSET
# ==========================================

@router.patch(
    "/{asset_id}",
    response_model=BrandAssetResponse
)
def update_brand_asset(
    asset_id: int,
    asset_data: BrandAssetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("MANAGE_BRAND_ASSETS")
    )
):

    asset = db.query(BrandAsset).filter(
        BrandAsset.id == asset_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Brand asset not found."
        )

    update_data = asset_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No valid fields provided for update."
        )

    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)

    return asset


# ==========================================
# DEACTIVATE BRAND ASSET
# ==========================================

@router.delete("/{asset_id}")
def deactivate_brand_asset(
    asset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("MANAGE_BRAND_ASSETS")
    )
):

    asset = db.query(BrandAsset).filter(
        BrandAsset.id == asset_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Brand asset not found."
        )

    asset.is_active = False

    db.commit()

    return {
        "message": "Brand asset deactivated successfully."
    }


# ==========================================
# ANALYZE BRAND ASSET IMAGE
# ==========================================

@router.post("/{asset_id}/analyze-image")
def analyze_image_endpoint(
    asset_id: int,
    request: ImageAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_user_permission("MANAGE_BRAND_ASSETS")
    )
):

    asset = db.query(BrandAsset).filter(
        BrandAsset.id == asset_id,
        BrandAsset.is_active.is_(True),
        BrandAsset.is_approved.is_(True)
    ).first()

    if not asset:
        raise HTTPException(
            status_code=404,
            detail="Approved brand asset not found."
        )

    try:

        image_path = resolve_asset_image_path(
            asset.file_path
        )

        if not image_path.exists():
            raise FileNotFoundError(
                "Brand asset image does not exist."
            )

        return analyze_brand_image(
            asset=asset,
            approved_colors=request.approved_colors,
            alt_text=request.alt_text,
            foreground_color=request.foreground_color,
            background_color=request.background_color,
            is_large_text=request.is_large_text
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Image analysis failed."
        )
