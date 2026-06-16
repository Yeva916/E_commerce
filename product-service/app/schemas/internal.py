from pydantic import BaseModel, Field
from uuid import UUID

class InternalProductResponse(BaseModel):
    id: UUID
    name: str
    price: float
    stock_quantity: int
    category_id: int
    is_active: bool

class InventoryResponse(BaseModel):
    product_id:UUID=Field(validation_alias='id')
    available_quantity:int=Field(validation_alias='stock_quantity')

    class Config:
        from_attributes=True

class ReservationSchema(BaseModel):
    product_id:UUID
    quantity:int

class ReservationResponse(BaseModel):
    product_id:UUID
    reserved_quantity:int
    remaining_quantity:int

class ReleaseSchema(BaseModel):
    product_id:UUID
    quantity:int

class ReleaseResponse(BaseModel):
    product_id: UUID
    released_quantity: int
    remaining_quantity: int

class Stock(BaseModel):
    product_id:UUID