from fastapi import APIRouter

from src.api.schemas.admin import InvitationCreate
from src.authentication import send_invitation_email_route

invitation_router = APIRouter()


@invitation_router.post("/invitation", name="auth:invitation", tags=["Admin Invitation"])
async def send_invitation_email_route_handler(invitation_create: InvitationCreate):
    return await send_invitation_email_route(invitation_create)
