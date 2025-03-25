from typing import Annotated

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status

from config.settings import settings
from db.session import get_db
from domains.auth.oauth.get_current_user import oauth2_scheme
from domains.auth.services.user import user_service


async def validate_refresh_token(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception

    except JWTError:
        raise credentials_exception
    user = await user_service.get_user_by_username(db=db, username=username)
    if user is None: raise credentials_exception

    return user, token
