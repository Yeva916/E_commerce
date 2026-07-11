from datetime import datetime,timezone
from uuid import UUID,uuid4
from pydantic import BaseModel,Field

from .event_types import EventType

class BaseEvent(BaseModel):
    
    event_id:UUID=Field(default_factory=uuid4)
    event_type:EventType
    occurred_at:datetime = Field(default_factory=lambda:datetime.now(timezone.utc))