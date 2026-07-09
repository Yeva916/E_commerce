from fastapi import APIRouter
from fastapi import Depends

from app.core.security import create_verification_token

# from app.services.auth_service import create_user,send_verification_email
from app.services.auth_service import AuthService
from app.api.dependency import get_auth_service
from app.schemas.user import UserCreate, UserResponse



router = APIRouter(prefix="/auth")


@router.post("/register",response_model=UserResponse)
async def register_user(user: UserCreate, auth_service:AuthService=Depends(get_auth_service)):
    try:
        user_data = await auth_service.create_user(user)
        email = user_data.email
        email_token = create_verification_token(email) 
        # send_verification_email(email,email_token)
    except Exception as e:
        raise Exception(f"Error occured during registraion:{e}")

    return {
            "message": "User registered successfully. Please check your email to verify your account.(remove email token from here only testing)",
            "id": user_data.id,
            "email": user_data.email,
            "username": user_data.username,
            "email_token":email_token
        }