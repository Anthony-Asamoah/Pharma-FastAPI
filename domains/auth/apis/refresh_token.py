from datetime import timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from config.settings import settings
from db.session import get_db
from domains.auth.utils.create_token import create_access_token, create_refresh_token
from domains.auth.utils.validate_refresh_token import validate_refresh_token

refresh_token_router = APIRouter()


class RefreshTokenSchema(BaseModel):
    refresh_token: str


@refresh_token_router.post("/refresh", status_code=status.HTTP_200_OK)
async def get_new_access_token(payload: RefreshTokenSchema, db: Session = Depends(get_db)):
    user, token = await validate_refresh_token(payload.refresh_token, db=db)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRES_IN)

    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    refresh_token = await create_refresh_token(data={"sub": user.username}, expires_delta=refresh_token_expires)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "status": status.HTTP_200_OK
    }
