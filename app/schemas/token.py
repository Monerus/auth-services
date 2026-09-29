from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class VerifyCode(BaseModel):
    email: EmailStr
    code: str