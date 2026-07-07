from fastapi import APIRouter,Request,Response
from app.clients.auth_client import auth_request
# from app.core.config import settings

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth Gateway"]
)

@router.api_route(
    "/{path:path}",
    methods=["GET","POST","PUT","DELETE","PATCH"]
)
async def auth_proxy(
    path:str,
    request:Request
):
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host",None)

    shared_client = request.app.state.http_client
    # print(path)
    response = await auth_request(
        client=shared_client,
        method=request.method,
        path=path,
        content=body,
        headers = headers,
        params = dict(request.query_params)
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type")
    )