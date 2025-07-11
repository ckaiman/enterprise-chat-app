from pydantic import BaseModel
from typing import Optional

class Office(BaseModel):
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfoResponse(BaseModel):
    email: str
    name: str
    role: str
    office: Optional[Office] = None