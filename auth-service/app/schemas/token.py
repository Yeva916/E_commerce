from uuid import UUID

from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
class TokenPayload(BaseModel):
    sub: UUID
    email:str
    role: str 