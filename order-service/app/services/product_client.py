
import httpx
from app.core.config import settings
from app.schemas.order import Item, ReleaseSchema, ReservationSchema
from pydantic import TypeAdapter
from typing import List
class ProductClient:
    def __init__(self):
        self.base_url = settings.product_service_url
    
    async def _request(self,client:httpx.AsyncClient,method:str,endpoint:str,**kwargs):
        headers = {"X-User-Role":"service"}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs
        )
        response.raise_for_status()

        return response.json()
        
    
    async def get_product(self,product_id):
        self._request("")


    async def get_stock(self,client,product_ids):
        # payload = [{"product_id":product_id for product_id in product_ids}]
        return await self._request(
                    client=client,
                    method="POST",
                    endpoint="/internal/products/stock",
                    json=product_ids
        )
    async def reserve_stock(self,client,payloads:ReservationSchema):
        adapter = TypeAdapter(List[ReservationSchema]) # this is used to dump the classes to json
        json_payload = adapter.dump_python(payloads, mode="json")
        return await self._request(
            client=client,
            method="POST",
            endpoint="/internal/products/reserve",
            json=json_payload
        )

    async def release_stock(self,client,payloads:ReleaseSchema):
        adapter = TypeAdapter(List[ReleaseSchema])
        json_payload = adapter.dump_python(payloads,mode="json")
        return await self._request(
            client=client,
            method="POST",
            endpoint="/internal/products/release",
            json = json_payload
        )