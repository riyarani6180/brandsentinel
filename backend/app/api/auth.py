
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr, TypeAdapter, ValidationError

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.security.password import get_password_hash, verify_password
from app.security.token import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    email = str(user_data.email).strip().lower()

    existing_user = db.query(User).filter(
        func.lower(User.email) == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    new_user = User(
        full_name=user_data.full_name,
        email=email,
        hashed_password=get_password_hash(user_data.password),
        role="CREATOR",
        is_active=True
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )

    return new_user


# --------------------------------------------------
# LOGIN WITH AUTOMATIC CREATOR REGISTRATION
# --------------------------------------------------

@router.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username.strip().lower()
    password = form_data.password

    # Validate email format
    try:
        TypeAdapter(EmailStr).validate_python(email)

    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address"
        )

    # Validate password length
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 6 characters"
        )

    # Find existing account (case-insensitive)
    user = db.query(User).filter(
        func.lower(User.email) == email
    ).first()

    if user:

        # Verify password for existing Admin and Creator accounts
        if not verify_password(
            password,
            user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check account status
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This user account is inactive"
            )

    else:

        # Automatically create a new Creator account
        new_user = User(
            full_name=email.split("@")[0][:150],
            email=email,
            hashed_password=get_password_hash(password),
            role="CREATOR",
            is_active=True
        )

        db.add(new_user)

        try:
            db.commit()
            db.refresh(new_user)
            user = new_user

        except IntegrityError:
            db.rollback()

            # Handle simultaneous registration attempts
            user = db.query(User).filter(
                func.lower(User.email) == email
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Account creation conflict. Please try again."
                )

            if not verify_password(
                password,
                user.hashed_password
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user account is inactive"
                )

        except Exception:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to create your account. Please try again."
            )

    # Generate JWT token with actual database role
    access_token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role
        }
    }
