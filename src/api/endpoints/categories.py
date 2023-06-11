from fastapi import APIRouter, Depends

from src.api.schemas import CategoryResponse, CategoryRequest
from src.api.services import CategoryService
from src.core.db.models import Category

api_router = APIRouter()


@api_router.get(
    "/",
    response_model=list[CategoryResponse],
    response_model_exclude_none=True,
    description="Получает список всех категорий.",
)
async def get_categories(category_service: CategoryService = Depends()) -> list[CategoryResponse]:
    return await category_service.get_all()


@api_router.post("/", description="Актуализирует список категорий.")
async def actualize_categories(
    categories: list[CategoryRequest], category_service: CategoryService = Depends()
) -> None:
    await category_service.actualize_objects(categories, Category)
