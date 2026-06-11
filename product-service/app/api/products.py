from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db


router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/")
def get_products(db:Session = Depends(get_db)):
    return {"message": "Get all products"}


@router.post("/")
def create_product(db:Session = Depends(get_db)):
    return {"message": "Create a new product"}


@router.get("/{product_id}")
def get_product(product_id:int,db:Session = Depends(get_db)):
    return {"message": f"Get product with id {product_id}"}


@router.put("/{product_id}")
def update_product(product_id:int,db:Session = Depends(get_db)):
    return {"message": f"Update product with id {product_id}"}

@router.delete("/{product_id}")
def delete_product(product_id:int,db:Session = Depends(get_db)):
    return {"message": f"Delete product with id {product_id}"}
