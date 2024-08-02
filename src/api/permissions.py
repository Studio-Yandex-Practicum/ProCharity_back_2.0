from src.api.fastapi_admin_users import fastapi_admin_users
from src.settings import settings

is_active_user = fastapi_admin_users.current_user(optional=settings.DEBUG, active=True)
is_active_superuser = fastapi_admin_users.current_user(optional=settings.DEBUG, active=True, superuser=True)
