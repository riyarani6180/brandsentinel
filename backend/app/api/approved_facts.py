
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.approved_fact import ApprovedFact
from app.models.user import User
from app.schemas.approved_fact import (
    ApprovedFactCreate,
    ApprovedFactUpdate,
    ApprovedFactResponse,
)
from app.security.dependencies import get_current_user
from app.security.permissions import require_permission


router = APIRouter(
    prefix="/approved-facts",
    tags=["Approved Facts"]
)


def validate_fact_expiry(valid_until: date | None):
    """
    Prevent creation or activation of expired approved facts.
    """
    if valid_until is not None and valid_until < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create or activate an expired approved fact."
        )


# CREATE APPROVED FACT - BRAND_ADMIN ONLY
@router.post(
    "/",
    response_model=ApprovedFactResponse,
    status_code=status.HTTP_201_CREATED
)
def create_approved_fact(
    fact_data: ApprovedFactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(
        current_user.role,
        "MANAGE_APPROVED_FACTS"
    )

    validate_fact_expiry(fact_data.valid_until)

    fact = ApprovedFact(**fact_data.model_dump())

    db.add(fact)
    db.commit()
    db.refresh(fact)

    return fact


# VIEW ALL APPROVED FACTS - ALL AUTHENTICATED USERS
@router.get(
    "/",
    response_model=list[ApprovedFactResponse]
)
def get_approved_facts(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ApprovedFact)

    if active_only:
        query = query.filter(
            ApprovedFact.is_active.is_(True)
        )

    return (
        query.order_by(ApprovedFact.id.desc())
        .all()
    )


# VIEW ONE APPROVED FACT - ALL AUTHENTICATED USERS
@router.get(
    "/{fact_id}",
    response_model=ApprovedFactResponse
)
def get_approved_fact(
    fact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    fact = db.query(ApprovedFact).filter(
        ApprovedFact.id == fact_id
    ).first()

    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved fact not found"
        )

    return fact


# UPDATE APPROVED FACT - BRAND_ADMIN ONLY
@router.put(
    "/{fact_id}",
    response_model=ApprovedFactResponse
)
def update_approved_fact(
    fact_id: int,
    fact_data: ApprovedFactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(
        current_user.role,
        "MANAGE_APPROVED_FACTS"
    )

    fact = db.query(ApprovedFact).filter(
        ApprovedFact.id == fact_id
    ).first()

    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved fact not found"
        )

    update_data = fact_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update information provided."
        )

    new_valid_until = update_data.get(
        "valid_until",
        fact.valid_until
    )

    new_is_active = update_data.get(
        "is_active",
        fact.is_active
    )

    if new_is_active:
        validate_fact_expiry(new_valid_until)

    for field, value in update_data.items():
        setattr(fact, field, value)

    db.commit()
    db.refresh(fact)

    return fact


# DEACTIVATE APPROVED FACT - BRAND_ADMIN ONLY
@router.delete("/{fact_id}")
def deactivate_approved_fact(
    fact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    require_permission(
        current_user.role,
        "MANAGE_APPROVED_FACTS"
    )

    fact = db.query(ApprovedFact).filter(
        ApprovedFact.id == fact_id
    ).first()

    if not fact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approved fact not found"
        )

    fact.is_active = False

    db.commit()

    return {
        "message": "Approved fact deactivated successfully",
        "fact_id": fact_id
    }
