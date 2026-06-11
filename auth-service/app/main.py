from fastapi import FastAPI
from app.api import register,login,users
from app.db.database import engine,Base

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(register.router)
app.include_router(login.router)
app.include_router(users.router)

@app.get("/")
def get_root():
    return {"message": "Welcome to the Auth Service"}