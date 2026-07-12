from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password,create_password_reset_token,UserRole
from app.schemas.token import TokenPayload,Token
# import resend
from app.models.user import User
from app.core.config import settings
from fastapi import HTTPException
from app.repository.auth_repository import AuthRepository
from app.schemas.user import UserCreate, UserLogin,ResetPasswordRequest
from app.events.publisher import EventPublisher
from jose import jwt, JWTError
from contracts.events.event_types import EventType
from contracts.events.registry import EVENT_REGISTRY


class AuthService:
    def __init__(self,auth_repository:AuthRepository,publisher:EventPublisher):
        self.auth_repository = auth_repository
        self.publisher = publisher

    def decode(self,tokens):
        try:
            payload = jwt.decode(tokens.strip().strip('"'), settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        return payload
    
    async def create_user(self,user:UserCreate):
        return await self.auth_repository.create_user(user)

    async def authenticate_user(self,user:UserLogin):
        user_db = await self.auth_repository.get_user_by_email(user.email)
        if not user:
            raise ValueError("Invalid email or password")
        if not verify_password(user.password, user_db.hashed_password):
            raise ValueError("Invalid email or password")
        if not user_db.is_verified:
            raise ValueError("Email is not verified. Please verify your email before logging in.")
        
        jwt_payload = TokenPayload(sub=user_db.id,email=user_db.email,role=user_db.role).model_dump()
        access_token = create_access_token(jwt_payload)
        refresh_token = create_refresh_token(jwt_payload)
        return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    
    async def send_verification_email(self,to_email:str,verification_token:str):
        class_ = EVENT_REGISTRY[EventType.USER_REGISTERED]
        event = class_(
            email = to_email,
            verification_token=verification_token
        )
        await self.publisher.publish(
            queue_name="email_queue",
            event=event
            )
    
    async def send_password_reset_email(self,to_email:str,reset_token:str):
        class_ = EVENT_REGISTRY[EventType.PASSWORD_RESET]
        # print(reset_token)
        event = class_(
            email=to_email,
            reset_token=reset_token
        )
        
        await self.publisher.publish(
            queue_name="email_queue",
            event=event
        )

    async def authenticate_or_register_google_user(self,email,google_id,username):
        return await self.auth_repository.authenticate_or_register_google_user(email,google_id,username)
    
    async def verify_user_email(self,tokens):
        try:
            payload = self.decode(tokens)
        except Exception as e:
            raise e
        
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token payload")
        
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.is_verified:
            return {"message": "Email is already verified"}
        verification_data = {"is_verified":True}
        return await self.auth_repository.update_user_details(email,verification_data)

    async def get_user_by_email(self,email):
        return await self.auth_repository.get_user_by_email(email)
    
    async def reset_password(self,token_id:str,data:ResetPasswordRequest):
        try:
            payload = self.decode(token_id)
            email:str = payload.get("sub")
        except Exception as e:
            raise e
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User with this email does not exist")
        update_data = {
            "hashed_password":hash_password(data.new_password)
        }
        await self.auth_repository.update_user_details(email,update_data)
        return {"message": "Password reset successful"}
    
    async def generate_reset_token(self,email):
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User with this email does not exist")
        
        reset_token = create_password_reset_token(user.email)
        return reset_token


    async def get_access_tokens_from_refresh_tokens(self,tokens):
        try:
            payload = self.decode(tokens)
            email:str = payload.get("email")
        except Exception as e:
            raise e
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_access_token = create_access_token(TokenPayload(sub=user.id,email=user.email,role=user.role).model_dump())
        return new_access_token
    
    async def get_current_user_from_token(self, token: str) -> User:
        """
        Decodes the access token and fetches the corresponding user record.
        Raises ValueError if the token is invalid or the user is missing.
        """
        try:
            payload = self.decode(token)
        except Exception as e:
            raise e

        user_id= payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")
        
        user = await self.auth_repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        return user
    
    async def promote_user_to_admin(self,user_id):
        user = await self.auth_repository.get_user_by_id(user_id=user_id)
        user = await self.auth_repository.update_user_details(user.email,{
            "role":UserRole.ADMIN
        })
        return user

    async def demote_admin_to_user(self,user_id):
        user = await self.auth_repository.get_user_by_id(user_id=user_id)
        user = await self.auth_repository.update_user_details(user.email,{
            "role":UserRole.CUSTOMER
        })
        return user