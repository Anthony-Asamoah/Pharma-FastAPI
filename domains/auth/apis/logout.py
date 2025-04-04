from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette import status

from db.session import get_db
from domains.auth.models import User
from domains.auth.utils import get_current_user
from domains.auth.services.user import user_service

logout_router = APIRouter()


@logout_router.get(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT
)
async def logout(
        request: Request,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user),
) -> None:
    token = request.headers.get("authorization").strip()
    token = token.replace("Bearer ", "")
    await user_service.logout(db=db, token=token)
