from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.order import Orders,OrderItem
from app.schemas.order import Item
from typing import List

class OrderRepository:
    def __init__(self,db:AsyncSession):
        self.db = db
    
    
    async def create_order(self,user_id,total_amount,status):
        order = Orders(
            user_id=user_id,
            status=status,
            total_amount=total_amount)
        
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def create_order_items(self,order_id,items:List[Item]):
        orders = [OrderItem(**item.model_dump(),order_id=order_id) for item in items]
        self.db.add_all(orders)
        await self.db.commit()
        # for order in orders:
        #     await self.db.refresh(order)
        return orders
    
    async def get_order_by_id(self,order_id):
        query = select(Orders).where(Orders.order_id == order_id)
        results = await self.db.execute(query)
        return results.scalars().first()

    async def get_order_by_user(self,user_id):
        query = (
            select(Orders)
            .where(Orders.user_id == user_id)
            .options(selectinload(Orders.items))
        )
        results = await self.db.execute(query)
        return results.scalars().all()
    
