from fastapi import APIRouter,Depends
from app.schemas.order import CreateOrderRequest
import httpx
from app.services.product_client import ProductClient
from app.core.dependency import get_http_client,get_product_client
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.order_repo import OrderRepository
from app.services.order_service import OrderService
router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)
def get_order_service(db:AsyncSession=Depends(get_db),
                      product_client:ProductClient = Depends(get_product_client),
                      http_client:httpx.AsyncClient = Depends(get_http_client)
                      ) -> OrderService:
    order_repo = OrderRepository(db)
    return OrderService(order_repo,product_client,http_client)

@router.post("/create-order")
async def create_order(
    payload:CreateOrderRequest,
    order_service:OrderService = Depends(get_order_service)
    ):
    user_id = payload.user_id
    order_items = payload.items
    return await order_service.create_order(user_id,order_items)
    