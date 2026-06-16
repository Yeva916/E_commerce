from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy.future import select
from app.models.products import Product
from app.schemas.product import ProductCreate,ProductUpdate
from typing import Dict, Literal
from sqlalchemy import asc,desc
from typing import List,Tuple,Dict

class ProductRepository:
    def __init__(self,db:AsyncSession):
        self.db = db

    async def create_product(self,products_data:ProductCreate)->Product:
        
        db_products = [Product(**product_data.model_dump()) for product_data in products_data]
        self.db.add_all(db_products)
        await self.db.commit()
        for db_product in db_products:
            await self.db.refresh(db_product)
        return db_products
    
    async def get_product_by_id(self,product_id:UUID)->Product:
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def list_products(self,
                            page:int,size:int,
                            search:str|None=None,
                            category_id:int|None=None,
                            min_price:float|None=None,
                            max_price:float|None=None,
                            sort_by:Literal["price_asc", "price_desc", "newest", "relevance"]=None
                            )->list[Product]:
        query = select(Product)
        if search:
            clean_search = search.strip()
            query = query.where(Product.name.icontains(clean_search))
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)
        if sort_by == "newest":
            query=query.order_by(desc(Product.created_at))
        elif sort_by=="price_asc":
            query=query.order_by(asc(Product.price))
        elif sort_by == "price_desc":
            query=query.order_by(desc(Product.price))
        elif sort_by == "relevance" or sort_by is None:
            query=query.order_by(desc(Product.id))
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

    async def update_product(
            self,
            product_id:UUID,
            product_data:ProductUpdate
        ) -> Product:
        query = select(Product).where(Product.id == product_id).with_for_update()
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
    
    # async def delete_product(self,product_id:UUID)->list[Product]:
    #     query = select(Product).where(Product.id == product_id)
    #     result = await self.db.execute(query)
    #     db_product = result.scalars().first()
    #     if not db_product:
    #         return None
    #     await self.db.delete(db_product)
    #     await self.db.commit()
    #     return db_product

    async def bulk_get_product_by_ids(self,product_ids:List[UUID]):
        query = select(Product).where(Product.id.in_(product_ids))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def bulk_decrease_stock(self,payloads)->Tuple[List[Product],Dict[UUID,int]]:

        product_ids = [p.product_id for p in payloads]
        payload_map = {p.product_id:p.quantity for p in payloads}

        try:
            query = (
                select(Product)
                .where(Product.id.in_(product_ids))
                .with_for_update()
            )

            result = await self.db.execute(query)
            products = result.scalars().all()

            if len(products) != len(product_ids):
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more products in your order do not exist."
            )

            for product in products:
                requested_qty = payload_map[product.id]
                if product.stock_quantity < requested_qty:
                    raise HTTPException (
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail = f"Insufficient stock for product: {product.name}"
                    )
            
            for product in products:
                product.stock_quantity -= payload_map[product.id]

            await self.db.commit()
            return products,payload_map
        
        except Exception as e:
            await self.db.rollback()
            raise e
    
    async def bulk_increase_stock(self,payloads)->Tuple[List[Product],Dict[UUID,int]]:

        product_ids = [p.product_id for p in payloads]
        payload_map = {p.product_id:p.quantity for p in payloads}

        try:
            query = (
                select(Product)
                .where(Product.id.in_(product_ids))
                .with_for_update()
            )

            result = await self.db.execute(query)
            products = result.scalars().all()

            if len(products) != len(product_ids):
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more products in your order do not exist."
            )

            # for product in products:
            #     requested_qty = payload_map[product.id]
            #     if product.stock_quantity < requested_qty:
            #         raise HTTPException (
            #             status_code=status.HTTP_400_BAD_REQUEST,
            #             detail = f"Insufficient stock for product: {product.name}"
            #         )
            
            for product in products:
                product.stock_quantity += payload_map[product.id]

            await self.db.commit()
            return products,payload_map
        
        except Exception as e:
            await self.db.rollback()
            raise e