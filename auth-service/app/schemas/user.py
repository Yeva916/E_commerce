
from uuid import UUID

from pydantic import BaseModel, Field,EmailStr,model_validator


class UserCreate(BaseModel):
    email: str
    username: str
    password: str = Field(..., min_length=8 ,max_length=72)

class UserResponse(BaseModel):
    message: str
    id: UUID
    email: str
    username: str
    email_token:str
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str = Field(..., min_length=8 ,max_length=72)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8 ,max_length=72)
    confirm_password: str = Field(..., min_length=8 ,max_length=72)

    @model_validator(mode='after')
    def check_passwords_match(self,)->'ResetPasswordRequest':
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self

