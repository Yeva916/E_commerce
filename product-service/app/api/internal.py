from fastapi import APIRouter, Depends
from app.schemas.internal import ReservationSchema,ReleaseSchema,ReservationResponse,ReleaseResponse,InternalProductResponse,InventoryResponse
from app.api.products import get_product_service
from app.services.product_service import ProductService
from uuid import UUID
from app.core.security import RoleChecker,UserRole
router = APIRouter(
    prefix="/internal/products",
    tags=["internal"]
)

@router.get("/{product_id}",response_model=InternalProductResponse,dependencies=[Depends(RoleChecker([UserRole.SERVICE]))])
async def get_product(product_id:UUID,product_service:ProductService=Depends(get_product_service)):
    print(product_id)
    result = await product_service.get_product_by_id(product_id)
    return result


@router.get("/{product_id}/stock",response_model=InventoryResponse,dependencies=[Depends(RoleChecker([UserRole.SERVICE]))])
async def check_stock(product_id:UUID,
                product_service:ProductService=Depends(get_product_service)):
    result = await product_service.get_product_by_id(product_id)
    return result


@router.post("/{product_id}/reserve",response_model=ReservationResponse,dependencies=[Depends(RoleChecker([UserRole.SERVICE]))]) #when the order is placed
async def reserve_product(product_id:UUID,
                          payload:ReservationSchema,
                          product_service:ProductService=Depends(get_product_service)
                          ):
    result = await product_service.decrease_stock(product_id,payload.quantity)
    return ReservationResponse(
        product_id=result.id,
        reserved_quantity=payload.quantity,
        remaining_quantity=result.stock_quantity)

@router.post("/{product_id}/release",response_model=ReleaseResponse,dependencies=[Depends(RoleChecker([UserRole.SERVICE]))]) #if user cancels the order
async def release_product(product_id:UUID,
                    payload:ReleaseSchema,
                    product_service:ProductService=Depends(get_product_service)):
    result = await product_service.increase_stock(product_id,payload.quantity)
    return ReleaseResponse(
        product_id=result.id,
        remaining_quantity=result.stock_quantity,
        released_quantity=payload.quantity)


