from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import CategoryRequest, CategoryResponse
from src.api.services import CategoryService
from src.core.db.models import Category
from src.core.depends.container import Container

category_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


@category_router.get(
    "/",
    response_model=list[CategoryResponse],
    response_model_exclude_none=True,
    description="Получает список всех категорий.",
)
@inject
async def get_categories(
    category_service: CategoryService = Depends(Provide[Container.api_services_container.category_service]),
) -> list[CategoryResponse]:
    return await category_service.get_all()


@category_router.post("/", description="Актуализирует список категорий.")
@inject
async def actualize_categories(
    categories: list[CategoryRequest],
    category_service: CategoryService = Depends(Provide[Container.api_services_container.category_service]),
) -> None:
    await category_service.actualize_objects(categories, Category)
