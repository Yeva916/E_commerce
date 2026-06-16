import httpx
# import
from fastapi import HTTPException,status
from app.schemas.order import Item, ReservationSchema
from app.repository.order_repo import OrderRepository
from app.services.product_client import ProductClient
from app.core.utils import cal_total_amount
from uuid import UUID
from typing import List
class OrderService:
    def __init__(self,order_repository:OrderRepository,product_client:ProductClient,http_client:httpx.AsyncClient):
        self.order_repository = order_repository
        self.product_client = product_client
        self.http_client = http_client

    async def create_order(self,user_id,items:List[Item]):
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
                order.status = "CONFIRMED"
                await self.order_repository.db.commit()
            except Exception as e:
                print(f"Stock reservation failed, marking order as FAILED: {e}")
                order.status = "FAILED"
                await self.order_repository.db.commit() # Save the failure state
                
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
            self.order_repository.get_order_by_id(order_id=order_id)
        except:
            print("Error while fetching order")

    async def get_user_orders(self,user_id):
        try:
            self.order_repository.get_order_by_user(user_id)
        except:
            print("Error while fetching the order details of the user")

    async def cancel_order(self,order_id):
        pass

    