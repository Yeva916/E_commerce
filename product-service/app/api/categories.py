from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.category import Category


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/")
def get_categories(db:Session = Depends(get_db)):
    return db.query(Category).all()


@router.post("/")
async def create_category(db:Session = Depends(get_db)):
    pass


@router.get("/{category_id}")
def get_category(category_id:int,db:Session = Depends(get_db)):
    return {"message": f"Get category with id {category_id}"}


@router.put("/{category_id}")
def update_category(category_id:int,db:Session = Depends(get_db)):
    return {"message": f"Update category with id {category_id}"}

@router.delete("/{category_id}")
def delete_category(category_id:int,db:Session = Depends(get_db)):
    return {"message": f"Delete category with id {category_id}"}
