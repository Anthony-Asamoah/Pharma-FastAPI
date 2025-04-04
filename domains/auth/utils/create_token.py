from datetime import timedelta
from typing import Optional

import pendulum
from jose import jwt

from config.settings import settings


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = pendulum.now() + expires_delta
    else:
        expire = pendulum.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = pendulum.now() + expires_delta
    else:
        expire = pendulum.now() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
