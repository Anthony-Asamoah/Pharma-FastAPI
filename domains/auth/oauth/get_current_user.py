from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config.settings import settings
from db.session import get_db
from domains.auth.services.revoked_token import revoked_token_service
from domains.auth.services.user import user_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user_by_username(db=db, username=username)
    if user is None: raise credentials_exception
    if not user.is_active: raise credentials_exception
    if user.is_deleted: raise credentials_exception

    is_blacklisted = await revoked_token_service.get_revoked_token_by_jti(db=db, jti=token.strip())
    print("is_blacklisted", is_blacklisted)
    if is_blacklisted: raise credentials_exception
    return user
