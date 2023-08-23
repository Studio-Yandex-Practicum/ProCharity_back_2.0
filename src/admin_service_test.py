import asyncio

from src.api.services.admin_service import AdminService


admin_service = AdminService()
data = {"email": "admin@example.com", "password": "password"}

access_token = admin_service.create_access_token(data)
print(access_token)


async def authenticate_currect():
    user = await admin_service.get_current_user(access_token)
    print(user)

asyncio.run(authenticate_currect())
