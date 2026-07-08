from typing import Annotated, List
from enum import Enum
from uuid import UUID
# from uuid import UUID
from fastapi import Header,HTTPException,status
import httpx
from app.services.product_client import ProductClient
# from app.repository.order_repo 
class UserRole(str,Enum):
    ADMIN="admin"
    CUSTOMER="user"
    SERVICE="service"
# The global singletons container dictionary
clients_state = {}

def get_http_client() -> httpx.AsyncClient:
    """Dependency injection target to fetch the open connection pool"""
    return clients_state["async_client"]

def get_product_client() -> ProductClient:
    """Dependency injection target to fetch the reusable ProductClient wrapper"""
    return clients_state["product_client"]


class RoleChecker:
    def __init__(self,allowed_roles=List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self,
                 x_user_role:Annotated[str|None,Header()]=None,
                 x_user_id:Annotated[UUID|None,Header()]=None
                 ):
        print(x_user_role,x_user_id)
        if x_user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to access this resource"
            )

        return x_user_id


