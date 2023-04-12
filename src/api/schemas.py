from pydantic import BaseModel, Field, Extra, root_validator
from typing import Optional


class CaregoryRequest(BaseModel):
    id: int = Field(..., ge=1, lt=10**10)
    name: str = Field(..., min_length=2, max_length=100)
    parent_id: Optional[int] = Field(None, ge=1, lt=10**10)

    class Config:
        extra = Extra.forbid

    @root_validator(skip_on_failure=True)
    def validate_self_parent(cls, values):
        if values['parent_id'] and values['parent_id'] == values['id']:
            raise ValueError('Категория не может быть дочерней для самой себя.')
        return values


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    archive: bool

    class Config:
        orm_mode = True
