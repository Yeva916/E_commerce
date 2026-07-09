from uuid import UUID
from app.api.dependency import read_current_user
from fastapi import APIRouter, Depends
from app.models.user import User
from app.core.security import RoleChecker, UserRole
from app.services.auth_service import AuthService
from app.api.dependency import get_auth_service
router = APIRouter(prefix="/auth")



@router.get("/users/me")
def get_me(current_user: User = Depends(read_current_user)):
    return current_user

@router.post("/users/{user_id}/promote",dependencies=[Depends(RoleChecker([UserRole.OWNER]))])
async def promote_to_admin(
    user_id:UUID,
    auth_service:AuthService=Depends(get_auth_service)
):
    return await auth_service.promote_user_to_admin(user_id)

@router.post("/users/{user_id}/demote",dependencies=[Depends(RoleChecker([UserRole.OWNER]))])
async def demote_to_user(
        user_id:UUID,
        auth_service:AuthService=Depends(get_auth_service)
):
    return await auth_service.demote_admin_to_user(user_id)