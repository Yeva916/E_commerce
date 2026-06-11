from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.schemas.category import InputCategory
class CategoryRepository:
    def __init__(self, db:AsyncSession):
        self.db = db

    async def get_category_by_id(self, category_id: int)->Category:
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_category_by_name(self, name: str)->Category:
        query = select(Category).where(Category.name == name)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def create_category(self,input:InputCategory)->Category:
        category = Category(**input.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def get_all_categories(self)->list[Category]:
        query = select(Category)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_category(self,category:Category,input:InputCategory)->Category:
        update_dict = input.model_dump(exclude_unset=True)
        for key,value in update_dict.items():
            setattr(category,key,value)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    
    async def archive_category(self,category:Category)->Category:
        category.is_archived = True
        await self.db.commit()
        await self.db.refresh(category)
        return category
