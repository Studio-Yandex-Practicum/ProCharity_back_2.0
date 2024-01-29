from pydantic import BaseModel

class TokenCheckResponse(BaseModel):
    description: str

    class Config:
        from_attributes = True