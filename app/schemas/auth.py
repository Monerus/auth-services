from pydantic import BaseModel, ConfigDict, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr


class UserResponse(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
    # code: str



class EmailRequest(BaseModel):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class VerifyCode(BaseModel):
    email: EmailStr
    # code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"