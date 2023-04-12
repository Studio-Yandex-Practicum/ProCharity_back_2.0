from fastapi import APIRouter, Depends

from src.api.schemas import CaregoryRequest, CategoryResponse
from src.core.services.category_service import CategoryService

router = APIRouter()
category_router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@category_router.get(
    "/",
    response_model=list[CategoryResponse],
    response_model_exclude_none=True,
    description="Получает список всех категорий.",
)
async def get_category(category_service: CategoryService = Depends()):
    categories = await category_service.get_all_categories()
    return categories


@category_router.post("/", description="Актуализирует список категорий.")
async def actualize_categories(categories: list[CaregoryRequest], category_service: CategoryService = Depends()):
    await category_service.actualize_categories(categories)
