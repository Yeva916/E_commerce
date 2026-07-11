import json
from aio_pika import IncomingMessage
from contracts.events.event_types import EventType
from contracts.events.registry import EVENT_REGISTRY

from app.dispatcher.event_dispatcher import EventDispatcher
from app.core.rabbitmq import RabbitMQClient
class EmailConsumer:
    def __init__(self,dispatcher:EventDispatcher,rabbitmq:RabbitMQClient):
        self.dispatcher = dispatcher
        self.rabbitmq = rabbitmq
    async def consume(self):

        if self.rabbitmq.channel is None:
            raise RuntimeError("Rabbit channel is not initialized")

        queue = await self.rabbitmq.channel.declare_queue(
            "email_queue",
            durable=True
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.process_message(message)
    
    async def process_message(
            self,
            message:IncomingMessage
    ):
        async with message.process():
            try:
                payload = json.loads(
                    message.body.decode("utf-8")
                )
                event_type = EventType(
                    payload["event_type"]
                )
                event_class = EVENT_REGISTRY[event_type]
                event = event_class.model_validate(payload)
                await self.dispatcher.dispatch(event)
            except Exception:
                raise "Failed to process RabbitMQ message"

# consumer = EmailConsumer()