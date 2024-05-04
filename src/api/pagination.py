import math


def paginate(objects: list, count_objects: int, page: int, limit: int, url: str) -> dict:
    """Формирование данных для пагинации."""
    pages = math.ceil(count_objects / limit) if count_objects else None
    next_page = page + 1 if page != pages else None
    previous_page = page - 1 if page != 1 else None
    next_url = f"{url}?page={next_page}&limit={limit}" if next_page else None
    previous_url = f"{url}?page={previous_page}&limit={limit}" if previous_page else None

    pagination_data = {
        "total": count_objects,
        "pages": pages,
        "current_page": page,
        "next_page": next_page,
        "previous_page": previous_page,
        "next_url": next_url,
        "previous_url": previous_url,
        "result": objects,
    }
    return pagination_data
