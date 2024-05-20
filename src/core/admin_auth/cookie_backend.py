from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy

from src.api.constants import COOKIE_LIFETIME_SECONDS
from src.settings import settings

cookie_transport = CookieTransport(cookie_max_age=COOKIE_LIFETIME_SECONDS)


def get_jwt_cookie_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=COOKIE_LIFETIME_SECONDS)


auth_cookie_backend = AuthenticationBackend(
    name="auth_cookie_backend",
    transport=cookie_transport,
    get_strategy=get_jwt_cookie_strategy,
)
