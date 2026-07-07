from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx
from app.routes import auth,orders,products
from app.middleware.auth_middleware import AuthMiddleware
@asynccontextmanager
async def lifespan(app:FastAPI):
    print("intializing System lifespan")
    async_client = httpx.AsyncClient(follow_redirects=True)
    app.state.http_client = async_client
    yield
    print("💤 Shutting down API Gateway: Closing client pool...")
    await async_client.aclose()

app = FastAPI(lifespan=lifespan,redirect_slashes=False)
app.add_middleware(AuthMiddleware)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.get("/")
def get_root():
    return {"message":"Welcome to Gateway"}