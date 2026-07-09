import httpx
# import
from fastapi import HTTPException,status
from app.schemas.order import Item, ReleaseSchema, ReservationSchema
from app.repository.order_repo import OrderRepository
from app.services.product_client import ProductClient
from app.core.utils import cal_total_amount
from uuid import UUID
from typing import List
from app.models.order import OrderStatus
# from app.core.utils import OrderStatus
class OrderService:
    def __init__(self,order_repository:OrderRepository,product_client:ProductClient,http_client:httpx.AsyncClient):
        self.order_repository = order_repository
        self.product_client = product_client
        self.http_client = http_client
    
    def is_authorized(self,current_user_id,owner_id):
        if owner_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not the who owns this order"
                )
    
    async def create_order(self,user_id,items:List[Item]):
        # user_id = current_user
        product_ids = [{"product_id":str(item.product_id)} for item in items]
        product_map = {
            item.product_id:{"quantity":item.quantity,
                             "price":item.price_at_purchase} 
                             for item in items}
        
        try:
            products = await self.product_client.get_stock(self.http_client,product_ids)
            # print(type(products[0]))
            for product in products:
                product_id = UUID(product["product_id"])
                if product["available_quantity"] < product_map[product_id]["quantity"]:
                    raise "Stock insufficient"
            
            
            total_amount = cal_total_amount(items)
            order = await self.order_repository.create_order(user_id,
                                                   total_amount,
                                                   status="PENDING")
            order_items = await self.order_repository.create_order_items(order.id,items)
            try:
                payloads = [ReservationSchema(product_id=item.product_id,quantity=item.quantity) for item in items]
                updated_products = await self.product_client.reserve_stock(self.http_client,payloads)
                # order.status = "CONFIRMED"
                # await self.order_repository.db.commit()
                await self.order_repository.update_order_status(order.id,OrderStatus.CONFIRMED)
            except Exception as e:
                print(f"Stock reservation failed, marking order as FAILED: {e}")
                # order.status = "FAILED"
                # await self.order_repository.db.commit() # Save the failure state
                await self.order_repository.update_order_status(order.id,OrderStatus.FAILED)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order placement failed during inventory reservation. Please try again."
            )
            return order_items,updated_products
            
        except HTTPException as http_exc:
        # Pass structured FastAPI HTTP errors straight through
            raise http_exc
        except Exception as e:
            print(f"Unexpected error while creating order: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating your order."
        )

    async def get_order(self,order_id):
        try:
            return await self.order_repository.get_order_by_id(order_id=order_id)
        except:
            print("Error while fetching order")

    async def get_user_orders(self,user_id):
        try:
            return await self.order_repository.get_order_by_user(user_id)
        except:
            print("Error while fetching the order details of the user")

    async def cancel_order(self,current_user_id,order_id):
        # order_owner_id = await self.order_repository.get_user_id_of_order(order_id)
        order = await self.order_repository.get_order_by_id(order_id)
        # print(order.id,order.status)
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order has already been cancelled."
            )
        # print(order_owner_id,current_user_id)
        self.is_authorized(current_user_id,order.user_id)
        try:
            order_items = await self.order_repository.get_order_items_by_order_id(order_id)
            payload = [ReleaseSchema(product_id=item.product_id,quantity=item.quantity) for item in order_items]
            updated_items = await self.product_client.release_stock(self.http_client,payload)
            await self.order_repository.update_order_status(order_id=order_id,status=OrderStatus.CANCELLED)

        except Exception as e:
             print(f"Unexpected error while creating order: {e}")
             raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating your order."
        )
        return updated_items