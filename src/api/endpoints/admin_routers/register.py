from typing import Type

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, status
from fastapi_users import BaseUserManager, models, schemas
from fastapi_users.manager import UserManagerDependency
from fastapi_users.router.common import ErrorModel

from src.api.schemas import TokenCheckResponse
from src.api.services import AdminTokenRequestService
from src.core.depends import Container
from src.core.exceptions.exceptions import InvalidInvitationToken, InvalidPassword, UserAlreadyExists


def get_register_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: Type[schemas.U],
    user_create_schema: Type[schemas.UC],
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        status_code=status.HTTP_200_OK,
        name="User Registration",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            UserAlreadyExists.status_code: {
                                "summary": "The user with the specified mailing address email is already registered.",
                                "value": {"detail": UserAlreadyExists.detail},
                            },
                            InvalidPassword.status_code: {
                                "summary": "The entered password does not comply with the password policy.",
                                "value": {"detail": InvalidPassword.detail},
                            },
                        }
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            InvalidInvitationToken.status_code: {
                                "summary": "The invitation token not found or expired.",
                                "value": {"detail": InvalidInvitationToken.detail},
                            },
                        }
                    }
                },
            },
        },
    )
    async def register(
        request: Request,
        user_create: user_create_schema,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        return await user_manager.create_with_token(user_create, safe=True, request=request)

    @router.post(
        "/token_checker",
        status_code=status.HTTP_200_OK,
        name="Checking invitation token.",
        responses={
            status.HTTP_403_FORBIDDEN: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            InvalidInvitationToken.status_code: {
                                "summary": "The invitation token not found or expired.",
                                "value": {"detail": InvalidInvitationToken.detail},
                            },
                        }
                    }
                },
            },
        },
    )
    @inject
    async def check_token(
        token: str,
        admin_token_request_service: AdminTokenRequestService = Depends(
            Provide[Container.api_services_container.admin_token_request_service]
        ),
    ):
        await admin_token_request_service.get_by_token(token)
        return TokenCheckResponse(description="Токен подтвержден.")

    return router
