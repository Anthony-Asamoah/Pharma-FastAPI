from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from db.session import get_db
from domains.auth.models import User
from domains.auth.oauth import get_current_user
from domains.auth.services.user import user_service

logout_router = APIRouter()


@logout_router.get("/logout", status_code=status.HTTP_200_OK)
async def logout(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return await user_service.logout(db=db, user=user)
