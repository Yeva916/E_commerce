
from fastapi import APIRouter,Request,Response
from app.clients.order_client import order_request

router = APIRouter(
    prefix="/api/orders",
    tags=["Order Gateway"]
)


@router.api_route(
    "/{path:path}",
    methods=["GET","POST","PUT","DELETE","PATCH"]
)
async def order_proxy(
    path:str="",
    request:Request=None
):
    body = await request.body()
    header = dict(request.headers)

    if hasattr(request.state,"user"):
        print(request.state.user["role"])
        header["X-User-ID"] = str(
            request.state.user["id"]
        )
    
        header["X-User-Role"] = (
            request.state.user["role"]
        )
        header["X-User-Email"]=(
            request.state.user["email"]
        )
        
    shared_client = request.app.state.http_client
    response = await order_request(
        client=shared_client,
        method=request.method,
        path=path,
        content=body,
        headers=header,
        params = dict(request.query_params)
    )
    return Response(
        content = response.content,
        status_code = response.status_code,
        media_type=response.headers.get("content-type")
    )