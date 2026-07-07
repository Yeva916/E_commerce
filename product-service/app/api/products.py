from uuid import UUID

from fastapi import APIRouter,Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.repository.product_repository import ProductRepository
from app.repository.category_repository import CategoryRepository
from app.services.product_service import ProductService
from app.services.category_service import CategoryService
from app.schemas.product import ChangeStockQuantity, ProductCreate, ProductResponse,ProductUpdate
from app.core.security import RoleChecker,UserRole
from typing import Annotated, Literal

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
    min_price:Annotated[int|None,Query(ge=0)]=None,
    max_price:Annotated[int|None,Query(ge=0)]=None,
    sort_by:Annotated[Literal["price_asc", "price_desc", "newest", "relevance"] | None, 
        Query(description="Sort order for results")
    ] = "newest",
    search:str|None=None,
    category_id:int|None=None,
    product_service:ProductService=Depends(get_product_service)
):
    results = await product_service.list_products(
        page=page,
        size=size,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by
    )
    return results


@router.post("/",response_model=list[ProductResponse],dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def create_product(product_data:list[ProductCreate],
                         product_service:ProductService=Depends(get_product_service)):
    created_product = await product_service.create_product(product_data)
    return created_product


@router.get("/{product_id}",response_model=ProductResponse,dependencies=[Depends(RoleChecker([UserRole.ADMIN,UserRole.CUSTOMER]))])
async def get_product(product_id:UUID,
                      product_service:ProductService=Depends(get_product_service)):
    result = await product_service.get_product_by_id(product_id)
    return result


@router.put("/{product_id}",response_model=ProductResponse,dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def update_product(product_id:UUID,
                         product_data:ProductUpdate,
                         product_service:ProductService=Depends(get_product_service)
                         ):
    updated_product = await product_service.update_product(product_id, product_data)
    return updated_product


@router.put("/{product_id}/archive",dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def delete_product(product_id:UUID,
                         product_service:ProductService=Depends(get_product_service)):
    archive_product = await product_service.archive_product(product_id)
    return archive_product

@router.post("/{product_id}/increase-stock",dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def increase_stock(product_id:UUID,
                        data:ChangeStockQuantity,
                        product_service:ProductService=Depends(get_product_service)
                        ):
    updated_stock = await product_service.increase_stock(product_id,data.quantity)
    return updated_stock

@router.post("/{product_id}/decrease-stock",dependencies=[Depends(RoleChecker([UserRole.ADMIN]))])
async def increase_stock(product_id:UUID,
                        data:ChangeStockQuantity,
                        product_service:ProductService=Depends(get_product_service)
                        ):
    updated_stock = await product_service.decrease_stock(product_id,data.quantity)
    return updated_stock
