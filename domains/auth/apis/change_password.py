from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models.user import User
from domains.auth.utils.get_current_user import get_current_user
from domains.auth.schemas.user import ChangePasswordSchema
from domains.auth.services.user import user_service

change_password_router = APIRouter(prefix='/users')


@change_password_router.post(
    "/change_password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        passwords_in: ChangePasswordSchema
) -> None:
    user_id = passwords_in.user_id or current_user.id
    return await user_service.change_password(db=db, user_id=user_id, passwords_in=passwords_in)
