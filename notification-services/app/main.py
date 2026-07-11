from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from app.consumers.email_consumer import EmailConsumer
from app.core.config import settings
from app.core.rabbitmq import RabbitMQClient
from app.core.container import container
rabbitmq = RabbitMQClient(settings.rabbitmq_url)
@asynccontextmanager
async def lifespan(app: FastAPI):
    #setup httpx client here and creat the container object here
    await rabbitmq.connect()
    
    dispatcher = container.event_dispatcher

    consumer = EmailConsumer(
        rabbitmq=rabbitmq,
        dispatcher=dispatcher
    )
    
    worker_task = asyncio.create_task(
        consumer.consume()
    )
    
    yield
    worker_task.cancel()
    await rabbitmq.close()

app = FastAPI(
    lifespan=lifespan
)

@app.get("/rabbitmq-health")
async def rabbitmq_health():

    return {
        "connected":rabbitmq.connection is not None,
        "channel":rabbitmq.channel is not None
    }
