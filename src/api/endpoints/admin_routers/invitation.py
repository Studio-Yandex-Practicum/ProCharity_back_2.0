from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from src.api.fastapi_admin_users import UserManager, get_admin_db
from src.api.permissions import is_active_superuser
from src.api.schemas.admin import InvitationCreateSchema
from src.api.services.admin_token_request import AdminTokenRequestService
from src.core.depends.container import Container
from src.core.exceptions import UserAlreadyExists
from src.core.services.email import EmailProvider

invitation_router = APIRouter(
    dependencies=[Depends(is_active_superuser)],
    responses={
        "401": {"description": "Missing token or inactive user"},
        "403": {"description": "Not superuser"},
    },
)


class InvitationManager(UserManager):
    async def create_invitation(
        self,
        email: str,
        is_superuser: bool,
        email_provider: EmailProvider = Depends(Provide[Container.core_services_container.email_provider]),
        admin_token_request_service: AdminTokenRequestService = Depends(
            Provide[Container.api_services_container.admin_token_request_service]
        ),
    ) -> None:
        existing_user = await self.user_db.get_by_email(email)
        if existing_user:
            raise UserAlreadyExists()
        invitation_token = await admin_token_request_service.create_invitation_token(email, is_superuser)
        await email_provider.send_invitation_link(email, invitation_token)


def get_invitation_manager(admin_db=Depends(get_admin_db)):
    yield InvitationManager(admin_db)


@invitation_router.post("/invitation", name="auth:invitation")
async def send_invitation_email_route(
    invitation_create: InvitationCreateSchema,
    invitation_manager: InvitationManager = Depends(get_invitation_manager),
):
    """
    Отправляет приглашение по электронной почте.
    """

    await invitation_manager.create_invitation(invitation_create.email, invitation_create.is_superuser)
    return {"detail": "Invitation e-mail has been sent successfully."}
