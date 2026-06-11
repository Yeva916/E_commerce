from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.database import get_db
from app.core.security import create_verification_token
from app.services.auth_service import create_user,send_verification_email
from app.schemas.user import UserCreate, UserResponse
router = APIRouter()

@router.post("/register",response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        user_data = create_user(user,db)
        # email = user_data.email
        # email_token = create_verification_token(email)
        # send_verification_email(email,email_token)
    except Exception as e:
        raise Exception(f"Error occured during registraion")

    return {
            "message": "User registered successfully. Please check your email to verify your account.",
            "id": user_data.id,
            "email": user_data.email,
            "username": user_data.username
        }