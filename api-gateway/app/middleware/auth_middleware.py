from urllib import response

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import HTTPException
from app.core.route_permissions import PUBLIC_ROUTES
from app.core.security import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        path = request.url.path
        method = request.method
        print(path,"middleware")
        if (method,path) in PUBLIC_ROUTES:
            print("hello")
            return await call_next(request)
        
        token = request.headers.get(
            "Authorization"
        )

        if not token:
            raise HTTPException(
                401,"Missing token"
            )

        token = token.replace(
            "Bearer ",""
        )

        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                401,
                "Invalid token"
            )

        request.state.user = {
            "id":payload["sub"],
            "role":payload["role"],
            "email":payload["email"]
        }

        response = await call_next(request)

        return response