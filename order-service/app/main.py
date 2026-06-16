from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.product_client import ProductClient
import httpx
from app.db.database import engine,Base
from app.core.dependency import clients_state
from app.api import orders

state = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts up
    print("🚀 Initializing system lifespan: Creating database tables...")
    async with engine.begin() as conn:
        # Creates tables if they don't exist yet
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database synchronization complete!")
    async_client = httpx.AsyncClient()
    product_client = ProductClient()
    clients_state["async_client"] = async_client
    clients_state["product_client"] = product_client
    print("🔌 Reusable HTTP network pools initialized successfully!")
    yield  
    print("💤 Shutting down system lifespan: Tearing down open sockets...")
    await async_client.aclose()
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.include_router(orders.router)

# def get_http_client() -> httpx.AsyncClient:
#     return state["async_client"]

# def get_product_client()-> ProductClient:
#     return state["product_client"]