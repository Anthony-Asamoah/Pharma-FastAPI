from datetime import timedelta
from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config.settings import settings
from db.session import get_db
from domains.auth.oauth.authenticate_user import authenticate_user
from domains.auth.oauth.create_token import create_refresh_token, create_access_token
from domains.auth.schemas.token import Token

login_router = APIRouter()


@login_router.post("/login")
async def get_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db)
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN)

    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token = await create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user,
        roles=user.get_roles(),
        permissions=user.get_permissions()
    )
