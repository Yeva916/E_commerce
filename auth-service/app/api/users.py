from uuid import UUID
from app.api.dependency import read_current_user
from fastapi import APIRouter, Depends
from app.models.user import User

router = APIRouter(prefix="/auth")



@router.get("/users/me")
def get_me(current_user: User = Depends(read_current_user)):
    return current_user

@router.get("/users/{user_id}/promote")
async def promote_to_admin(
    user_id:UUID
):
    pass