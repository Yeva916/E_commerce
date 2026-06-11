from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"]
)

@router.get("/{product_id}")
def get_inventory(product_id:int,db:Session = Depends(get_db)):
    return {"message": f"Get inventory for product with id {product_id}"}

@router.patch("/{product_id}")
def update_inventory(product_id:int,db:Session = Depends(get_db)):
    return {"message": f"Update inventory for product with id {product_id}"}