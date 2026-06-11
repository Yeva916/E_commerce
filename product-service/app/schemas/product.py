
from pydantic import BaseModel
from uuid import UUID


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category_id: int

class ProductResponse(BaseModel):
    id: UUID
    name: str
    price: float
    
    class Config:
        from_attributes = True