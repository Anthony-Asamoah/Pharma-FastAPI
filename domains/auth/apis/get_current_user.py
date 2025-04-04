from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from domains.auth.models import User
from domains.auth.utils import get_current_user
from domains.auth.schemas.user import UserSchema
from domains.auth.services.user import user_service

current_user_router = APIRouter(prefix="/users")


@current_user_router.get("/me", response_model=UserSchema)
async def get_current_user_details(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await user_service.get_user(db=db, id=current_user.id)
