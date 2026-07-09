from fastapi import HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import hash_password
from app.models.user import User,AuthProvider
class AuthRepository:
    def __init__(self,db:AsyncSession):
        self.db =db

    async def get_user_by_email(self,email):
        query = select(User).where(User.email==email)
        result = await self.db.execute(query)  
        return result.scalars().first()

    async def create_user(self,user):
        # print("hi")
        is_email_used = await self.get_user_by_email(user.email)
        # print(is_email_used)
        if is_email_used:
            raise ValueError("Email is already used")
        user_data = user.dict()
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        new_user = User(**user_data)
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self,user_id):
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def authenticate_or_register_google_user(self,email,google_id,username):
        user_data = {
            "provider_user_id":google_id,
            "auth_provider":AuthProvider.GOOGLE,
            "is_verified":True
        }
        user = await self.update_user_details(email,user_data)
        if not user:
            user = User(
                email=email,
                username=username,
                auth_provider=AuthProvider.GOOGLE,
                provider_user_id=google_id,
                is_verified=True  # Google users are pre-verified
            )
            self.db.add(user)
            await self.db.commit()          # Await the commit for the new user insertion
            await self.db.refresh(user)     # Await the refresh to populate the DB-generated fields (like ID)
        return user
    
    async def update_user_details(self,email,user_data):
        query = select(User).where(User.email==email).with_for_update()
        result = await self.db.execute(query)  
        user = result.scalars().first()
        if user is None:
            return None
        # update_data = user_data.model_dump(exclude_unset=True)
        for key,value in user_data.items():
            if hasattr(user,key):
                setattr(user,key,value)
        await self.db.commit()
        await self.db.refresh(user)
        return user