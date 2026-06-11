from uuid import UUID

from fastapi import APIRouter,Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repository.product_repository import ProductRepository
from app.repository.category_repository import CategoryRepository
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.schemas.product import ProductCreate, ProductResponse,ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

def get_product_service(db:AsyncSession=Depends(get_db))->ProductService:
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)
    category_service = CategoryService(category_repo)
    return ProductService(product_repo,category_service)

@router.get("/",response_model=list[ProductResponse])
async def get_products(
    page:int=Query(1,ge=1),
    size:int=Query(20,ge=1,le=100),
    search:str|None=None,
    category_id:int|None=None,
    product_service:ProductService=Depends(get_product_service)
):
    results = await product_service.list_products(
        page=page,
        size=size,
        search=search,
        category_id=category_id
    )
    return results


@router.post("/",response_model=ProductResponse)
async def create_product(product_data:ProductCreate,
                         product_service:ProductService=Depends(get_product_service)):
    created_product = await product_service.create_product(product_data)
    return created_product


@router.get("/{product_id}",response_model=ProductResponse)
async def get_product(product_id:UUID,
                      product_service:ProductService=Depends(get_product_service)):
    result = await product_service.get_product_by_id(product_id)
    return result


@router.put("/{product_id}",response_model=ProductResponse)
async def update_product(product_id:UUID,
                         product_data:ProductUpdate,
                         product_service:ProductService=Depends(get_product_service)
                         ):
    updated_product = await product_service.update_product(product_id, product_data)
    return updated_product


@router.delete("/{product_id}")
async def delete_product(product_id:UUID,
                         product_service:ProductService=Depends(get_product_service)):
    deleted_product = await product_service.delete_product(product_id)
    return deleted_product
