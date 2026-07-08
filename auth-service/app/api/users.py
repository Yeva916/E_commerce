from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.security import decode_access_token

router = APIRouter(prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") # this responsible for the authorize button in the docs
# @router.get("/users/me")
def read_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id= int(payload.get("sub"))
  
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.get("/users/me")
def get_me(current_user: User = Depends(read_current_user)):
    return current_user

@router.get("/users/{user_id}/promote")
async def promote_to_admin(
    user_id:UUID
):
    pass