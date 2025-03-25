from typing import Annotated

from fastapi import HTTPException, Depends, status

from domains.auth.models.user import User
from domains.auth.oauth.get_current_user import get_current_user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_active: raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Account requires activation."
    )
    return current_user
