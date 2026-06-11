from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import products, categories, inventory
from app.db.database import engine,Base
from app.models.products import Product
from app.models.category import Category


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts up
    print("🚀 Initializing system lifespan: Creating database tables...")
    async with engine.begin() as conn:
        # Creates tables if they don't exist yet
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database synchronization complete!")
    yield  
    
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(inventory.router)

@app.get("/")
def get_root():
    return {"message": "Welcome to the Auth Service"}