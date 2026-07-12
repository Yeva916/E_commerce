
from fastapi import APIRouter, Depends, HTTPException,Response,Request
from fastapi.responses import RedirectResponse
from app.schemas.token import TokenPayload, TokenResponse
from app.schemas.user import ForgotPasswordRequest, ResetPasswordRequest, UserLogin
from app.services.auth_service import AuthService
from app.core.config import settings
import httpx
from app.api.dependency import get_auth_service
from app.core.security import create_access_token,create_refresh_token
router = APIRouter(prefix="/auth")

# dont forget to change the redirect url in the google app 
@router.get("/login")
def login_page():
    return {"welcome to login page"}
@router.post("/login",response_model=TokenResponse)
async def login_with_password(user:UserLogin, response: Response,auth_service:AuthService=Depends(get_auth_service)):
    user = await auth_service.authenticate_user(user)
    
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
                    auth_service:AuthService=Depends(get_auth_service)):
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
        
        # user = db.query(User).filter(User.email == email).first()

        # if user:
        #     need_commit = False
        #     if hasattr(user,"auth_provider") and user.auth_provider!= AuthProvider.GOOGLE:
        #         user.auth_provider = AuthProvider.GOOGLE
        #         user.provider_user_id = google_id
        #         need_commit = True
        #         # db.commit()
        #     if hasattr(user,"is_verified") and not user.is_verified:
        #         user.is_verified = True
        #         need_commit = True
        #     if need_commit:
        #         db.commit()
        #         db.refresh(user)
        # else:
        #     user = User(
        #         email=email,
        #         username=username,
        #         auth_provider=AuthProvider.GOOGLE,
        #         provider_user_id=google_id,
        #         is_verified = 1
        #     )
        #     db.add(user)
        #     db.commit()
        #     db.refresh(user)
        user = auth_service.authenticate_or_register_google_user(email,google_id,username)
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
async def verify_email(token:str,auth_service:AuthService=Depends(get_auth_service)):    
    await auth_service.verify_user_email(token)
    return RedirectResponse(url="/auth/login")


@router.post("/forgot-password")
async def forgot_password(data:ForgotPasswordRequest,
                          auth_service:AuthService=Depends(get_auth_service)):
    reset_token = await auth_service.generate_reset_token(data.email) 
    return await auth_service.send_password_reset_email(data.email,reset_token)

@router.post("/{token_id}/reset-password")
async def reset_password(
                        token_id:str,
                        data:ResetPasswordRequest, 
                        auth_service:AuthService=Depends(get_auth_service)):
    
    return await auth_service.reset_password(token_id,data)

@router.get("/refresh-tokens",response_model=TokenResponse)
async def refresh_tokens(request:Request,auth_service:AuthService=Depends(get_auth_service)):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    new_access_token = await auth_service.get_access_tokens_from_refresh_tokens(refresh_token)
    return TokenResponse(access_token=new_access_token, token_type="bearer")


