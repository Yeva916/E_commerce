import httpx
from app.core.config import settings

async def order_request(
        client:httpx.AsyncClient,
        method:str,
        path:str,
        content:None,
        params=None,
        headers=None
):
    response = await client.request(
        method=method,
        url=f"{settings.order_service_url}/orders/{path}",
        content=content,
        headers=headers,
        params=params
    )
    return response