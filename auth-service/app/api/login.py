
from fastapi import APIRouter, Depends, HTTPException,Response,Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.token import Token, TokenPayload, TokenResponse
from app.schemas.user import ForgotPasswordRequest, ResetPasswordRequest, UserLogin
from jose import jwt, JWTError
from app.models.user import User, AuthProvider
from app.services.auth_service import authenticate_user
from app.core.config import settings
import httpx
from app.core.security import create_access_token,hash_password,create_password_reset_token,create_refresh_token
router = APIRouter()

@router.post("/login",response_model=TokenResponse)
def login_with_password(user:UserLogin, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(user, db)
    
    access_token = user.access_token
    refresh_token = user.refresh_token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return TokenResponse(access_token=access_token, token_type="bearer")

@router.get("/login/google")
def login_with_google():
    # Implement Google OAuth login logic here
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(url=google_auth_url)

@router.get("/google/callback")
async def google_callback(response:Response,code:str=None,
                    error:str=None,
                    db:Session=Depends(get_db)):
    if error:
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            }
        )

        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange code for token")
        
        token_data = token_response.json()
        google_access_token = token_data.get("access_token")

        uuserinfo_response = await client.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {google_access_token}"}
        )

        if uuserinfo_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
        
        google_user = uuserinfo_response.json()
        email = google_user.get("email")
        google_id = google_user.get("id")
        username = google_user.get("name")
        
        user = db.query(User).filter(User.email == email).first()

        if user:
            need_commit = False
            if hasattr(user,"auth_provider") and user.auth_provider!= AuthProvider.GOOGLE:
                user.auth_provider = AuthProvider.GOOGLE
                user.provider_user_id = google_id
                need_commit = True
                # db.commit()
            if hasattr(user,"is_verified") and not user.is_verified:
                user.is_verified = True
                need_commit = True
            if need_commit:
                db.commit()
                db.refresh(user)
        else:
            user = User(
                email=email,
                username=username,
                auth_provider=AuthProvider.GOOGLE,
                provider_user_id=google_id,
                is_verified = 1
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        payload = TokenPayload(sub=user.id,email=user.email,role=user.role).model_dump()

        jwt_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax"
        )

        return {
            "message":"Successfully logged in via Google!",
            "access_token":jwt_token,
            "token_type":"bearer",
            "user":{
                "id":user.id,
                "email":user.email,
                "username":user.username
            }
        }

@router.get("/verify-email")
def verify_email(token:str,db:Session=Depends(get_db)):
    try:
        print(token)
        token = token.strip().strip('"')
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        # payload = payload.strip('"')

        print(payload)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token payload")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        return {"message": "Email is already verified"}
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return RedirectResponse(url="/login")


@router.post("/forgot-password")
def forgot_password(data:ForgotPasswordRequest, db:Session=Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    
    # Generate password reset token
    reset_token = create_password_reset_token(user.email)
    # Here you would send the reset token to the user's email address
    # For demonstration, we'll just return the token in the response -> need to implement email sending logic here
    return {"message": "Password reset token generated. Please check your email.", "reset_token": reset_token}

@router.post("/reset-password")
def reset_password(data:ResetPasswordRequest, db:Session=Depends(get_db)):
    try:
        payload = jwt.decode(data.token.strip().strip('"'), settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email:str = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password reset successful"}

@router.get("/refresh-tokens",response_model=TokenResponse)
def refresh_tokens(request:Request,db:Session=Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    try:
        payload = jwt.decode(refresh_token.strip().strip('"'), settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id:str = payload.get("sub")
        email:str = payload.get("email")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_access_token = create_access_token(TokenPayload(sub=user.id,email=user.email,role=user.role).model_dump())

    return TokenResponse(access_token=new_access_token, token_type="bearer")


