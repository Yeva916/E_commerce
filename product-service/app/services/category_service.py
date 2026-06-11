from app.repository.category_repository import CategoryRepository
from fastapi import HTTPException
from app.schemas.category import InputCategory
from app.models.category import Category

class CategoryService:
    def __init__(self,repository:CategoryRepository):
        self.repository = repository
    
    async def create_category(self,category_data:InputCategory):
        existing_category = await self.repository.get_category_by_name(category_data.name)
        
        if existing_category:
            raise HTTPException(status_code=400,detail="Category with this name already exists")
        
        new_category = await self.repository.create_category(category_data)
        return new_category
    
    async def get_all_categories(self):
        results = await self.repository.get_all_categories()
        return results

    async def get_category_by_id(self,category_id:int):
        category = await self.repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404,detail="Category not found")
        return category

    async def update_category(self,category_id:int,input:InputCategory):
        category = await self.repository.get_category_by_id(category_id)
        if not category:
             raise HTTPException(status_code=400,detail="Category does not exist")
        category = await self.repository.update_category(category,input)
        if not category:
            raise HTTPException(status_code=404,detail="Category not found")
        return category

    async def archive_category(self,category_id:int):
        category = await self.repository.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404,detail="Category not found")
        archived_category = await self.repository.archive_category(category)
        return archived_category
