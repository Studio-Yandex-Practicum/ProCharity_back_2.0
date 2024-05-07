import math

from src.core.db.repository import AbstractRepository


async def paginate(repository: AbstractRepository, page: int, limit: int, url: str, format_objects=None) -> dict:
    """Формирование данных для пагинации."""
    objects = await repository.get_objects_by_page(page, limit)
    count_objects = await repository.count_all()

    if format_objects:
        result = []
        for object in objects:
            result.append(format_objects(object))
        objects = result

    pages = math.ceil(count_objects / limit)
    next_page = page + 1 if page < pages else None
    previous_page = page - 1 if page > 1 else None
    next_url = f"{url}?page={next_page}&limit={limit}" if next_page else None
    previous_url = f"{url}?page={previous_page}&limit={limit}" if previous_page else None

    return {
        "total": count_objects,
        "pages": pages,
        "current_page": page,
        "next_page": next_page,
        "previous_page": previous_page,
        "next_url": next_url,
        "previous_url": previous_url,
        "result": objects,
    }
