from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import AuthService
from app.services.auth_service import AuthService,AsyncEmailService
from app.repository.auth_repository import AuthRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from fastapi import  Request
import httpx
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") # this responsible for the authorize button in the docs
# @router.get("/users/me")

def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_auth_service(db:AsyncSession=Depends(get_db)) -> AuthService:
    email_service = AsyncEmailService(client=Depends(get_http_client))
    auth_repo = AuthRepository(db)
    return AuthService(auth_repo,email_service)

async def read_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service:AuthService=Depends(get_auth_service)
):
    try:
        # Call the new service method
        return await auth_service.get_current_user_from_token(token)
    except ValueError as e:
        # Catch business errors and translate them into clean HTTP status codes
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

