# from app.models.user import User
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password,create_password_reset_token
from app.schemas.token import TokenPayload,Token
# import resend
from app.models.user import User
from app.core.config import settings
from fastapi import HTTPException
from app.repository.auth_repository import AuthRepository
from app.schemas.user import UserCreate, UserLogin,ResetPasswordRequest
from app.services.email_services import AsyncEmailService
from jose import jwt, JWTError

# def create_user(user,db) -> User:
#     #check is the email is used or not
#     is_email_used = get_user_by_email(user.email,db)
#     if is_email_used:
#         raise ValueError("Email is already used")

#     user_data = user.dict()
#     user_data["hashed_password"] = hash_password(user_data.pop("password"))
#     new_user = User(**user_data)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

# def get_user_by_email(email,db) -> User:
#     return db.query(User).filter(User.email == email).first()


# def authenticate_user(user,db):
#     db_user = get_user_by_email(user.email,db)
#     if not db_user:
#         raise ValueError("Invalid email or password")
#     if not verify_password(user.password, db_user.hashed_password):
#         raise ValueError("Invalid email or password")
#     if not db_user.is_verified:
#         raise ValueError("Email is not verified. Please verify your email before logging in.")
#     jwt_payload = TokenPayload(sub=db_user.id,email=db_user.email,role=db_user.role).model_dump()
#     access_token = create_access_token(jwt_payload)
#     refresh_token = create_refresh_token(jwt_payload)
    
#     return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


# async def get_user_by_id(user_id,db):
#     query = db.query(User).fliter

# resend.api_key = settings.resend_api_key
# def send_verification_email(to_email:str, verification_token:str):
#     verification_link = f"{settings.base_url}/verify-email?token={verification_token}"
#     html_content = f"""
#     <html>
#         <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
#             <h2>Welcome to our E-commerce Store!</h2>
#             <p>Thank you for signing up. Please verify your email address to unlock your account and begin shopping.</p>
#             <div style="margin: 30px 0;">
#                 <a href="{verification_link}" 
#                    style="background-color: #000000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
#                     Verify Email Address
#                 </a>
#             </div>
#             <p style="font-size: 12px; color: #666;">This verification link will expire in 15 minutes.</p>
#             <p style="font-size: 12px; color: #666;">If the button above doesn't work, copy and paste this URL into your browser:</p>
#             <p style="font-size: 12px; color: #0066cc;">{verification_link}</p>
#         </body>
#     </html>
#     """

#     try:
#         resend.Emails.send({
#             "from":"onboarding@resend.dev",
#             "to":[to_email],
#             "subject":"Activate Your Account",
#             "html":html_content
#         })
#     except Exception as e:
#         raise Exception(f"Failed to send verification email: {e}")


# def send_password_reset_email(to_email:str, reset_token:str):
#     reset_link = f"{settings.base_url}/reset-password?token={reset_token}"
#     html_content = f"""
#     <html>
#         <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
#             <h2>Password Reset Request</h2>
#             <p>We received a request to reset your password. Click the button below to proceed.</p>
#             <div style="margin: 30px 0;">
#                 <a href="{reset_link}" 
#                    style="background-color: #000000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
#                     Reset Password
#                 </a>
#             </div>
#             <p style="font-size: 12px; color: #666;">This password reset link will expire in 15 minutes.</p>
#             <p style="font-size: 12px; color: #0066cc;">If the button above doesn't work, copy and paste this URL into your browser:</p>
#             <p style="font-size: 12px; color: #0066cc;">{reset_link}</p>
#         </body>
#     </html>
#     """

#     try:
#         resend.Emails.send({
#             "from":"onboarding@resend.dev",
#             "to":[to_email],
#             "subject":"Reset Your Password",
#             "html":html_content
#         })
#     except Exception as e:
#         raise Exception(f"Failed to send password reset email: {e}")
    
class AuthService:
    def __init__(self,auth_repository:AuthRepository,email_service:AsyncEmailService):
        self.auth_repository = auth_repository
        self.email_service = email_service

    def decode(self,tokens):
        try:
            payload = jwt.decode(tokens.strip().strip('"'), settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        # user_id:str = payload.get("sub")
        # email:str = payload.get("email")
        # role:str=payload.get("role")
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
        return await self.email_service.send_verification_email(to_email,verification_token)
    
    async def send_password_reset_email(self,to_emial:str,reset_token:str):
        return await self.email_service.send_password_reset_email(to_emial,reset_token)

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
        # user.hashed_password = hash_password(data.new_password)
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
        return {"message": "Password reset token generated. Please check your email.", "reset_token": reset_token}


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
            # 1. Clean token strings if needed
            payload = self.decode(token)
        except Exception as e:
            raise e


        # 2. Extract subject (user ID)
        user_id= payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        # 3. Retrieve user from the database via repository
        # (Assuming you updated your repository layer to use async queries)
        user = await self.auth_repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        return user