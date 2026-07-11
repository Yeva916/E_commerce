from pydantic import EmailStr

from .base import BaseEvent
from .event_types import EventType

class UserRegisteredEvent(BaseEvent):
    event_type:EventType = EventType.USER_REGISTERED
    email:EmailStr
    verification_token:str

class PasswordResetEvent(BaseEvent):
    event_type:EventType = EventType.PASSWORD_RESET
    email:EmailStr
    reset_token:str

