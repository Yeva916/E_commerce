
from uuid import UUID

from fastapi import APIRouter,Depends
from app.schemas.order import CreateOrderRequest,CancelOrderRequest
import httpx
from app.services.product_client import ProductClient
from app.core.dependency import get_http_client,get_product_client,RoleChecker,UserRole,get_event_producer
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.order_repo import OrderRepository
from app.services.order_service import OrderService
from app.events.publisher import EventPublisher
router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)
def get_order_service(db:AsyncSession=Depends(get_db),
                      product_client:ProductClient = Depends(get_product_client),
                      http_client:httpx.AsyncClient = Depends(get_http_client),
                      publisher:EventPublisher = Depends(get_event_producer)
                      ) -> OrderService:
    order_repo = OrderRepository(db)
    return OrderService(order_repo,product_client,http_client,publisher)

@router.post("/create-order")
async def create_order(
    payload:CreateOrderRequest,
    order_service:OrderService = Depends(get_order_service),
    user_details = Depends(RoleChecker([UserRole.ADMIN,UserRole.CUSTOMER,UserRole.OWNER]))
    ):
    # user_id = payload.user_id
    order_items = payload.items
    return await order_service.create_order(user_details["id"],order_items,user_details["email"])

@router.post("/{order_id}/cancel_order")
async def cancel_order(
    order_id:UUID,
    order_service:OrderService = Depends(get_order_service),
    user_details = Depends(RoleChecker([UserRole.ADMIN,UserRole.CUSTOMER,UserRole.OWNER]))
):
    return await order_service.cancel_order(user_details["id"],order_id,user_details["email"])

# @router.get("/")
# async def get_order_by_id(
#     id:UUID,
#     order_service:OrderService=Depends(get_order_service)
# ):
#     return await order_service.get

@router.get("/my_orders")
async def get_my_orders(
    user_details = Depends(RoleChecker([UserRole.ADMIN,UserRole.CUSTOMER,UserRole.OWNER])),
    order_service:OrderService = Depends(get_order_service)
):
    return await order_service.get_user_orders(user_details["id"])

# router.get("/{id}/")
