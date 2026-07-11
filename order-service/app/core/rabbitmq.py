import json

from aio_pika import RobustChannel,RobustConnection,Message
import aio_pika


class RabbitMQClient:
    def __init__(self,url:str):
        self.url = url
        self.connection:RobustConnection|None=None
        self.channel:RobustChannel|None=None

    async def connect(self):
        if self.connection:
            return 
        
        self.connection = await aio_pika.connect_robust(
            self.url
        )

        self.channel = await self.connection.channel()

    
    async def publish(
            self,
            queue_name:str,
            message:dict
    ):
        if self.channel is None:
            raise RuntimeError("RabbitMQ is not connected.")

        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json"
            ),
            routing_key=queue_name
        )    
    
    async def close(self):
        if self.connection:
            await self.connection.close()

            self.connection = None
            self.channel = None
    
