from app.models.user import User
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.schemas.token import TokenPayload,Token
import resend
from app.core.config import settings
resend.api_key = settings.resend_api_key
def create_user(user,db) -> User:
    #check is the email is used or not
    is_email_used = get_user_by_email(user.email,db)
    if is_email_used:
        raise ValueError("Email is already used")

    user_data = user.dict()
    user_data["hashed_password"] = hash_password(user_data.pop("password"))
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(email,db) -> User:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(user,db):
    db_user = get_user_by_email(user.email,db)
    if not db_user:
        raise ValueError("Invalid email or password")
    if not verify_password(user.password, db_user.hashed_password):
        raise ValueError("Invalid email or password")
    if not db_user.is_verified:
        raise ValueError("Email is not verified. Please verify your email before logging in.")
    jwt_payload = TokenPayload(sub=db_user.id,email=db_user.email,role=db_user.role).model_dump()
    access_token = create_access_token(jwt_payload)
    refresh_token = create_refresh_token(jwt_payload)
    
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")


async def get_user_by_id(user_id,db):
    query = db.query(User).fliter


def send_verification_email(to_email:str, verification_token:str):
    verification_link = f"{settings.base_url}/verify-email?token={verification_token}"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <h2>Welcome to our E-commerce Store!</h2>
            <p>Thank you for signing up. Please verify your email address to unlock your account and begin shopping.</p>
            <div style="margin: 30px 0;">
                <a href="{verification_link}" 
                   style="background-color: #000000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Verify Email Address
                </a>
            </div>
            <p style="font-size: 12px; color: #666;">This verification link will expire in 15 minutes.</p>
            <p style="font-size: 12px; color: #666;">If the button above doesn't work, copy and paste this URL into your browser:</p>
            <p style="font-size: 12px; color: #0066cc;">{verification_link}</p>
        </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from":"onboarding@resend.dev",
            "to":[to_email],
            "subject":"Activate Your Account",
            "html":html_content
        })
    except Exception as e:
        raise Exception(f"Failed to send verification email: {e}")


def send_password_reset_email(to_email:str, reset_token:str):
    reset_link = f"{settings.base_url}/reset-password?token={reset_token}"
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; color: #333;">
            <h2>Password Reset Request</h2>
            <p>We received a request to reset your password. Click the button below to proceed.</p>
            <div style="margin: 30px 0;">
                <a href="{reset_link}" 
                   style="background-color: #000000; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    Reset Password
                </a>
            </div>
            <p style="font-size: 12px; color: #666;">This password reset link will expire in 15 minutes.</p>
            <p style="font-size: 12px; color: #0066cc;">If the button above doesn't work, copy and paste this URL into your browser:</p>
            <p style="font-size: 12px; color: #0066cc;">{reset_link}</p>
        </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from":"onboarding@resend.dev",
            "to":[to_email],
            "subject":"Reset Your Password",
            "html":html_content
        })
    except Exception as e:
        raise Exception(f"Failed to send password reset email: {e}")
    
