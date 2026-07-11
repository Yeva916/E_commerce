from app.core.rabbitmq import RabbitMQClient
from contracts.events.base import BaseEvent

class EventPublisher:
    def __init__(self,rabbitmq:RabbitMQClient):
        self.rabbitmq = rabbitmq
    
    async def publish(self,queue_name:str,event:BaseEvent):
        await self.rabbitmq.publish(
            queue_name=queue_name,
            message=event.model_dump(mode="json")
        )
# publisher = EventPublisher()