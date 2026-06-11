
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

class ProductUpdate(BaseModel):
    name:str|None=None
    description:str|None=None
    price:float|None=None
    image_url:str|None=None
    stock_quantity:int|None=None
    is_archived:bool|None=None
    category_id:int|None=None
    