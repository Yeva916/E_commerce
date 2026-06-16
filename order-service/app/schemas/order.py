from typing import List
from uuid import UUID

from pydantic import BaseModel

class Item(BaseModel):
    product_id:UUID
    quantity:int
    price_at_purchase:float

class ReservationSchema(BaseModel):
    product_id:UUID
    quantity:int

class ReleaseSchema(BaseModel):
    product_id:UUID
    quantity:int

class CreateOrderRequest(BaseModel):
    user_id:UUID
    items :List[Item]