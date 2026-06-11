
from fastapi import Depends
from requests import Session
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.products import Product
from app.schemas.product import ProductCreate,ProductUpdate

class ProductRepository:
    def __init__(self,db:Session=Depends(get_db)):
        self.db = db

    async def create_product(self,product_data:ProductCreate):
        
        db_product = Product(**product_data.model_dump())
        await self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product
    
    async def get_product_by_id(self,product_id:UUID):
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all_products(self):
        query = select(Product)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_product(
            self,
            product_id:UUID,
            product_data:ProductUpdate
        ):
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        db_product = result.scalars().first()
        if not db_product:
            return None
        update_data = product_data.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(db_product,key,value)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product
    
    async def delete_product(self,product_id:UUID):
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        db_product = result.scalars().first()
        if not db_product:
            return None
        await self.db.delete(db_product)
        await self.db.commit()
        return db_product