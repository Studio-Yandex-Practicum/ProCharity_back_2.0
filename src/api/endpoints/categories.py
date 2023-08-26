from fastapi import APIRouter, Depends

from src.api.endpoints.constants import CATEGORY_POST_DESCRIPTION
from src.api.schemas import CategoryRequest, CategoryResponse
from src.api.services import CategoryService
from src.core.db.models import Category

category_router = APIRouter()


@category_router.get(
    "/",
    response_model=list[CategoryResponse],
    response_model_exclude_none=True,
    description="Получает список всех категорий.",
)
async def get_categories(category_service: CategoryService = Depends()) -> list[CategoryResponse]:
    return await category_service.get_all()


@category_router.post("/", description=CATEGORY_POST_DESCRIPTION)
async def actualize_categories(
    categories: list[CategoryRequest], category_service: CategoryService = Depends()
) -> None:
    await category_service.actualize_objects(categories, Category)
