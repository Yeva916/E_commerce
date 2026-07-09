from fastapi import FastAPI
import httpx
from app.api import register,login,users
from app.db.database import engine,Base
from contextlib import asynccontextmanager
# Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("🚀 Initializing system lifespan: Creating database tables...")
    async with engine.begin() as conn:
        # Creates tables if they don't exist yet
        await conn.run_sync(Base.metadata.create_all)
    async_client = httpx.AsyncClient()
    app.state.http_client = async_client
    print("✅ Database synchronization complete!")
    yield  
    
    await async_client.aclose()
    await engine.dispose()
    

app = FastAPI(lifespan=lifespan)


app.include_router(register.router)
app.include_router(login.router)
app.include_router(users.router)

@app.get("/")
def get_root():
    return {"message": "Welcome to the Auth Service"}