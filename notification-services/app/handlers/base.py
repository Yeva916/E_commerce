from abc import ABC,abstractmethod
from contracts.events.base import BaseEvent

class EventHandler(ABC):
    @classmethod
    @abstractmethod
    
    async def handle(self,event:BaseEvent):
        ...
