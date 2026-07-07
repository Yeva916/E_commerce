import httpx
from app.core.config import settings

async def auth_request(
        client:httpx.AsyncClient,
        method:str,
        path:str,
        content=None,
        params=None,
        headers=None
):
    # print(path)
    response = await client.request(
        method=method,
        url=f"{settings.auth_service_url}/auth/{path}",
        content=content,
        headers=headers,
        params=params
    )
    return response
