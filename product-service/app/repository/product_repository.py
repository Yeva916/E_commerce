
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy.future import select
from app.db.database import get_db
from app.models.products import Product
from app.schemas.product import ProductCreate,ProductUpdate

class ProductRepository:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_product(self,product_data:ProductCreate)->Product:
        
        db_product = Product(**product_data.model_dump())
        await self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product
    
    async def get_product_by_id(self,product_id:UUID)->Product:
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def list_products(self,page:int,size:int,search:str|None=None,category_id:int|None=None)->list[Product]:
        query = select(Product)
        if search:
            query = query.where(Product.name.contains(search))
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_product_by_name(self,name:str) -> Product:
        query = select(Product).where(Product.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all_products(self) -> list[Product]:
        query = select(Product)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def filter_products(self,
                              category_id:int|None=None,
                              min_price:float|None=None,
                              max_price:float|None=None,
                              )->list[Product]:
        query = select(Product)
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_product(
            self,
            product_id:UUID,
            product_data:ProductUpdate
        ) -> list[Product]:
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
    
    async def delete_product(self,product_id:UUID)->list[Product]:
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        db_product = result.scalars().first()
        if not db_product:
            return None
        await self.db.delete(db_product)
        await self.db.commit()
        return db_product