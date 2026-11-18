
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.security.token import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Identify the currently logged-in user
    using their JWT access token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    # Decode and verify the JWT token.
    payload = decode_access_token(token)

    user_id = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    # Safely convert the user ID.
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception

    # Retrieve the actual user from the database.
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive."
        )

    return user
