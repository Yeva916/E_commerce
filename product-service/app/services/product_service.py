from typing import List
from app.repository.product_repository import ProductRepository
from app.services.category_service import CategoryService
from fastapi import HTTPException
from app.schemas.product import ProductCreate,ProductUpdate
from uuid import UUID


class ProductService:
    def __init__(self,product_repository:ProductRepository,category_service:CategoryService):
        self.product_repository = product_repository
        self.category_service = category_service

    async def create_product(self,products_data:list[ProductCreate]):
        validated_products = []
        seen_name_in_batch = set()
        for product_data in products_data:
            if product_data.price <= 0:
                raise HTTPException(status_code=400,detail="Price must be a positive integer")
            
            existing_product = await self.product_repository.get_product_by_name(product_data.name)
            
            if existing_product:
                raise HTTPException(status_code=400,detail="Product with this name already exists")
            

            # I think i need to intergrate with category repository services rather than repository 
            category = await self.category_service.get_category_by_id(product_data.category_id)
            if not category:
                raise HTTPException(status_code=400,detail=f"Category with this {product_data.category_id} does not exist")
            seen_name_in_batch.add(product_data.name)
            validated_products.append(product_data)
            # new_product = await self.product_repository.create_product(product_data)
            # output_list.append(new_product)
        db_products = await self.product_repository.create_product(validated_products)
        return db_products

    async def get_product_by_id(self,product_id:UUID):
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404,detail="Product not found")
        return product
    
    async def list_products(self,
                            page,
                            size,
                            search:str|None=None,
                            category_id:int|None=None,
                            min_price:int|None=None,
                            max_price:int|None=None,
                            sort_by:str|None=None
                            ):
        if category_id is not None:
            category = await self.category_service.get_category_by_id(category_id)
            if not category:
                raise HTTPException(status_code=400,detail="Category with this id does not exist")
        
        products = await self.product_repository.list_products(page,
                                                               size,search=search,
                                                               category_id=category_id,
                                                               min_price=min_price,
                                                               max_price=max_price,
                                                               sort_by=sort_by
                                                               )
        return products

    async def update_product(self,product_id:UUID,product_data:ProductUpdate):
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404,detail="Product not found")
        
        if product_data.price is not None and product_data.price <= 0:
            raise HTTPException(status_code=400,detail="Price must be a positive integer")
        
        if product_data.name is not None and product_data.name != product.name:
            existing_product = await self.product_repository.get_product_by_name(product_data.name)
            if existing_product:
                raise HTTPException(status_code=400,detail="Product with this name already exists")
        
        if product_data.category_id is not None and product_data.category_id != product.category_id:
            category = await self.category_service.get_category_by_id(product_data.category_id)
            if not category:
                raise HTTPException(status_code=400,detail="Category with this id does not exist")
        
        updated_product = await self.product_repository.update_product(product_id,product_data)
        return updated_product
    
    async def increase_stock(self,product_id:UUID,quantity:int):
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404,detail="Product not found")
        update_product = await self.product_repository.update_product(
            product_id,
            ProductUpdate(stock_quantity=product.stock_quantity + quantity)
        )
        return update_product
    
    async def decrease_stock(self,product_id:UUID,quantity:int):
        product = await self.product_repository.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404,detail="Product not found")
        if product.stock_quantity < quantity:
            raise HTTPException(status_code=400,detail="Not enough stock available")
        update_product = await self.product_repository.update_product(
            product_id,
            ProductUpdate(stock_quantity=product.stock_quantity - quantity)
        )
        return update_product

    async def archive_product(self,product_id:UUID):
        product = await self.product_repository.get_product_by_id(product_id)
        
        if not product:
            raise HTTPException(status_code=404,detail="Product not found")
        result = await self.product_repository.update_product(
            product_id,
            ProductUpdate(is_active=False)
        )
        return result

    async def bulk_get_product_by_ids(self,product_ids):
        ids = []
        for id in product_ids:
            ids.append(id.product_id)
        return await self.product_repository.bulk_get_product_by_ids(ids)
    
    async def bulk_increase_stock(self,payloads):
        return await self.product_repository.bulk_increase_stock(payloads)
    
    async def bulk_decrease_stock(self,payloads):
        return await self.product_repository.bulk_decrease_stock(payloads)