
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.guideline import Guideline
from app.models.user import User
from app.schemas.guideline import (
    GuidelineCreate,
    GuidelineUpdate,
    GuidelineResponse,
)
from app.security.dependencies import get_current_user
from app.security.permissions import require_permission


router = APIRouter(
    prefix="/guidelines",
    tags=["Brand Guidelines"]
)


# CREATE GUIDELINE - BRAND_ADMIN ONLY
@router.post(
    "/",
    response_model=GuidelineResponse,
    status_code=status.HTTP_201_CREATED
)
def create_guideline(
    guideline_data: GuidelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(current_user.role, "MANAGE_GUIDELINES")

    guideline = Guideline(
        name=guideline_data.name,
        description=guideline_data.description,
        source_filename=guideline_data.source_filename,
        content=guideline_data.content
    )

    db.add(guideline)
    db.commit()
    db.refresh(guideline)

    return guideline


# VIEW ALL GUIDELINES - ALL AUTHENTICATED USERS
@router.get(
    "/",
    response_model=list[GuidelineResponse]
)
def get_guidelines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Guideline)
        .filter(Guideline.is_active == True)
        .order_by(Guideline.id.desc())
        .all()
    )


# VIEW ONE GUIDELINE - ALL AUTHENTICATED USERS
@router.get(
    "/{guideline_id}",
    response_model=GuidelineResponse
)
def get_guideline(
    guideline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    guideline = db.query(Guideline).filter(
        Guideline.id == guideline_id,
        Guideline.is_active == True
    ).first()

    if not guideline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guideline not found"
        )

    return guideline


# UPDATE GUIDELINE - BRAND_ADMIN ONLY
@router.put(
    "/{guideline_id}",
    response_model=GuidelineResponse
)
def update_guideline(
    guideline_id: int,
    guideline_data: GuidelineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(current_user.role, "MANAGE_GUIDELINES")

    guideline = db.query(Guideline).filter(
        Guideline.id == guideline_id,
        Guideline.is_active == True
    ).first()

    if not guideline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guideline not found"
        )

    update_data = guideline_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update information provided."
        )

    for field, value in update_data.items():
        setattr(guideline, field, value)

    guideline.version += 1

    db.commit()
    db.refresh(guideline)

    return guideline


# DEACTIVATE GUIDELINE - BRAND_ADMIN ONLY
@router.delete(
    "/{guideline_id}"
)
def deactivate_guideline(
    guideline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(current_user.role, "MANAGE_GUIDELINES")

    guideline = db.query(Guideline).filter(
        Guideline.id == guideline_id,
        Guideline.is_active == True
    ).first()

    if not guideline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Guideline not found"
        )

    guideline.is_active = False

    db.commit()

    return {
        "message": "Guideline deactivated successfully",
        "guideline_id": guideline_id
    }
