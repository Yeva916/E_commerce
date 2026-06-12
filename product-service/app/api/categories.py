from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.schemas.category import CategoryResponse,InputCategory
from app.services.category_service import CategoryService
from app.repository.category_repository import CategoryRepository
from app.core.security import RoleChecker,UserRole

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

def get_category_service(db:AsyncSession=Depends(get_db)):
    category_repo = CategoryRepository(db)
    return CategoryService(category_repo)

@router.get("/",response_model=list[CategoryResponse],dependencies=[Depends(RoleChecker([UserRole.ADMIN,UserRole.CUSTOMER]))])
async def get_categories(category_service:CategoryService=Depends(get_category_service)):
    categories = await category_service.get_all_categories()
    return categories


@router.post("/",response_model=CategoryResponse,dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def create_category(
                        category: InputCategory,
                        category_service:CategoryService=Depends(get_category_service)
                        ):
    
    created_category = await category_service.create_category(category)
    return created_category


@router.get("/{category_id}",response_model=CategoryResponse,dependencies=[Depends(RoleChecker([UserRole.ADMIN,UserRole.CUSTOMER]))])
async def get_category(
    category_id:int,
    category_service:CategoryService=Depends(get_category_service)
    ):

    category = await category_service.get_category_by_id(category_id)
    return category

@router.put("/{category_id}",response_model=CategoryResponse,dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def update_category(
    category_id:int,
    category: InputCategory,
    category_service:CategoryService=Depends(get_category_service)
    ):
    updated_category = await category_service.update_category(category_id, category)
    return updated_category

@router.delete("/{category_id}",response_model=CategoryResponse,dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def delete_category(
    category_id:int,
    category_service:CategoryService=Depends(get_category_service)
    ):
    deleted_category = await category_service.archive_category(category_id)
    return deleted_category
