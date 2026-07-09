from typing import Annotated,List
from fastapi import Header,HTTPException,status
from enum import Enum


class UserRole(str,Enum):
    ADMIN="admin"
    CUSTOMER="user"
    SERVICE="service"
    OWNER="owner"

class RoleChecker:
    def __init__(self,allowed_roles:List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self,x_user_role:Annotated[str|None,Header()]=None):
        # print(x_user_role)
        if not x_user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing user identity context from Gateway"
            )

        if x_user_role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return x_user_role