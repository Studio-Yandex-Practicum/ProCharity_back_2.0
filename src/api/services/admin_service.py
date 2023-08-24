import contextlib
from datetime import datetime, timedelta
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.core.db.models import AdminUser
from src.core.db.repository.admin_repository import AdminUserRepository
from src.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class AdminService:
    """Сервис для работы с моделью AdminUser."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def authenticate_user(self, email: str, password: str) -> AdminUser | None:
        async with self._sessionmaker() as session:
            repository = AdminUserRepository(session)
            user = await repository.get_by_email(email)
            if user and user.check_password(password):
                return user
            return None

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> AdminUser:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("email")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        async with self._sessionmaker() as session:
            repository = AdminUserRepository(session)
            user = await repository.get_by_email(email)
            if not user:
                raise credentials_exception
            return user
