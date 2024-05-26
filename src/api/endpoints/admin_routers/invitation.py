from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from src.api.fastapi_admin_users import UserManager, fastapi_admin_users, get_admin_db
from src.api.schemas.admin import InvitationCreateSchema
from src.api.services.admin_token_request import AdminTokenRequestService
from src.core.depends.container import Container
from src.core.exceptions.exceptions import UserAlreadyExists
from src.core.services.email import EmailProvider
from src.settings import settings

invitation_router = APIRouter(
    dependencies=[
        Depends(fastapi_admin_users.current_user(optional=settings.DEBUG)),
    ]
)


class InvitationManager(UserManager):
    async def create_invitation(
        self,
        email: str,
        email_provider: EmailProvider = Depends(Provide[Container.core_services_container.email_provider]),
        admin_token_request_service: AdminTokenRequestService = Depends(
            Provide[Container.api_services_container.admin_token_request_service]
        ),
    ) -> None:
        existing_user = await self.user_db.get_by_email(email)
        if existing_user:
            raise UserAlreadyExists()
        invitation_token = await admin_token_request_service.create_invitation_token(email)
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

    await invitation_manager.create_invitation(invitation_create.email)
    return {"detail": "Invitation e-mail has been sent successfully."}
