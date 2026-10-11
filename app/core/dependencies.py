from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database, models, oauth2


def require_admin(
    current_user: models.User = Depends(oauth2.get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user