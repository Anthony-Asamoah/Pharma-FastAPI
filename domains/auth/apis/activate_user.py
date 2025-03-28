from fastapi import APIRouter, status, Depends
from pydantic import UUID4
from sqlalchemy.orm import Session

from crud.base_schema import HTTPError
from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.auth.rbac import check_user_role
from domains.auth.services.user import user_service

activate_user_router = APIRouter(prefix="/user")


@activate_user_router.post(
    "/{id}/activate",
    name="activate_account",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
    dependencies=[Depends(check_user_role(["SystemAdmin", "Admin", "Manager"]))],
)
async def activate_user(
        *, db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        id: UUID4
) -> None:
    await user_service.activate_user(db=db, id=id)
