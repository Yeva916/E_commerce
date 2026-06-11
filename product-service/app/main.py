from fastapi import FastAPI
from app.api import products, categories, inventory
from app.db.database import engine,Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(products.router)
app.include_router(categories.router)
app.include_router(inventory.router)

@app.get("/")
def get_root():
    return {"message": "Welcome to the Auth Service"}