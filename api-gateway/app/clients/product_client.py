import httpx
from app.core.config import settings

async def product_request(
        client:httpx.AsyncClient,
        method:str,
        path:str,
        content:None,
        params=None,
        headers=None
):
    clean_path = path.lstrip("/")
    response = await client.request(
        method=method,
        url=f"{settings.product_service_url}/products/{clean_path}",
        content=content,
        headers=headers,
        params=params
    )
    return response