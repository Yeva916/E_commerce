from .auth import UserRegisteredEvent,PasswordResetEvent
from .order import OrderCreatedEvent
from .event_types import EventType

EVENT_REGISTRY = {
    EventType.USER_REGISTERED:UserRegisteredEvent,
    EventType.PASSWORD_RESET:PasswordResetEvent,
    EventType.ORDER_CREATED:OrderCreatedEvent
}