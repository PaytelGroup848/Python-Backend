from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRequest(BaseModel):

    email: EmailStr

    password: str

class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str

class RefreshTokenResponse(BaseModel):

    access_token: str

    token_type: str

class ChatRequest(BaseModel):

    session_id: Optional[str] = None

    message: str