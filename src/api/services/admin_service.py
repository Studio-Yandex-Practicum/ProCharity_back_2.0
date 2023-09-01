from datetime import datetime, timedelta

from jose import JWTError, jwt

from src.core.db.models import AdminUser
from src.core.db.repository.admin_repository import AdminUserRepository
from src.core.exceptions.exceptions import CredentialsException
from src.settings import settings


class AdminService:
    """Сервис для работы с моделью AdminUser."""

    def __init__(self, admin_repository: AdminUserRepository) -> None:
        self._repository: AdminUserRepository = admin_repository

    async def authenticate_user(self, email: str, password: str) -> AdminUser | None:
        user = await self._repository.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str) -> AdminUser:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("email")
            if email is None:
                raise CredentialsException("Don't have an email in the token")
        except JWTError:
            raise CredentialsException("Could not validate credentials(token)")
        user = await self._repository.get_by_email(email)
        if not user:
            raise CredentialsException("There is no user in db with such email")
        return user
