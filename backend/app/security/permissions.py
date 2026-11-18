
from fastapi import Depends, HTTPException, status

from app.security.dependencies import get_current_user


ROLE_PERMISSIONS = {
    "CREATOR": [
        "CREATE_SUBMISSION",
        "VIEW_OWN_SUBMISSION",
        "EDIT_OWN_SUBMISSION"
    ],

    "BRAND_MANAGER": [
        "VIEW_SUBMISSIONS",
        "REVIEW_SUBMISSIONS",
        "REQUEST_CHANGES"
    ],

    "AUTHORISED_REVIEWER": [
        "VIEW_SUBMISSIONS",
        "REVIEW_SUBMISSIONS",
        "APPROVE_SUBMISSIONS",
        "REJECT_SUBMISSIONS",
        "REQUEST_CHANGES",
        "REVIEW_HIGH_RISK_CONTENT"
    ],

    "BRAND_ADMIN": [
        "VIEW_SUBMISSIONS",
        "REVIEW_SUBMISSIONS",
        "APPROVE_SUBMISSIONS",
        "REJECT_SUBMISSIONS",
        "REQUEST_CHANGES",
        "REVIEW_HIGH_RISK_CONTENT",
        "MANAGE_USERS",
        "MANAGE_GUIDELINES",
        "MANAGE_APPROVED_FACTS",
        "MANAGE_BRAND_ASSETS",
        "VIEW_AUDIT_LOGS"
    ]
}


def check_permission(role: str, permission: str) -> bool:
    permissions = ROLE_PERMISSIONS.get(role, [])
    return permission in permissions


def require_permission(role: str, permission: str):
    if not check_permission(role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )


def require_user_permission(permission: str):
    def permission_dependency(
        current_user=Depends(get_current_user)
    ):
        require_permission(current_user.role, permission)
        return current_user

    return permission_dependency
