from fastapi import APIRouter, Depends
from app.schemas.internal import ReservationSchema,ReleaseSchema,ReservationResponse,ReleaseResponse,InternalProductResponse,InventoryResponse,Stock
from app.api.products import get_product_service
from app.services.product_service import ProductService
from uuid import UUID
from app.core.security import RoleChecker,UserRole
from typing import List
router = APIRouter(
    prefix="/internal/products",
    tags=["internal"]
)

# @router.get("/",response_model=List[InternalProductResponse],dependencies=[Depends(RoleChecker([UserRole.SERVICE]))])
# async def get_product(product_ids:List[UUID],product_service:ProductService=Depends(get_product_service)):
#     # print(product_id)
#     result = await product_service.bulck_get_product_by_ids(product_ids)
#     return result


@router.post("/stock",response_model=List[InventoryResponse],dependencies=[Depends(RoleChecker([UserRole.SERVICE]))])
async def check_stock(product_ids:List[Stock],
                product_service:ProductService=Depends(get_product_service)):

    # print(product_ids)
    result = await product_service.bulk_get_product_by_ids(product_ids)
    return result


@router.post("/reserve",response_model=List[ReservationResponse],dependencies=[Depends(RoleChecker([UserRole.SERVICE]))]) #when the order is placed
async def reserve_product(
                          payloads:List[ReservationSchema],
                          product_service:ProductService=Depends(get_product_service)
                          ):
    products,product_map = await product_service.bulk_decrease_stock(payloads) ## solve error
    response = []
    # print(products)
    for product in products:
        res = ReservationResponse(
        product_id=product.id,
        reserved_quantity=product_map[product.id], # solve error
        remaining_quantity=product.stock_quantity)
        # )
        response.append(res)
    return response

@router.post("/release",response_model=List[ReleaseResponse],dependencies=[Depends(RoleChecker([UserRole.SERVICE]))]) #if user cancels the order
async def release_product(
                    payload:List[ReleaseSchema],
                    product_service:ProductService=Depends(get_product_service)):
    products,product_map = await product_service.bulk_increase_stock(payload) # solve error
    response = []
    for product in products:
        res = ReleaseResponse(
        product_id=product.id,
        remaining_quantity=product.stock_quantity, #solve error
        released_quantity=product_map[product.id])
        response.append(res)
    return response


