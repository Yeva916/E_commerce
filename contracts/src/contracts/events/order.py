from uuid import UUID

from pydantic import EmailStr

from .base import BaseEvent
from .event_types import EventType

class OrderCreatedEvent(BaseEvent):
    event_type :EventType= EventType.ORDER_CREATED
    order_id:UUID
    email:EmailStr
    total_amount:float

