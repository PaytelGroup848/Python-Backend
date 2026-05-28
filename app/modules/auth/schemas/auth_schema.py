
from pydantic import (
    BaseModel,
    EmailStr
)

from typing import Optional


# =========================
# REGISTER
# =========================

class RegisterRequest(BaseModel):

    name: str

    email: EmailStr

    password: str


# =========================
# LOGIN
# =========================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# =========================
# TOKEN RESPONSE
# =========================

class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str


# =========================
# REFRESH TOKEN RESPONSE
# =========================

class RefreshTokenResponse(BaseModel):

    access_token: str

    token_type: str


# =========================
# CHAT REQUEST
# =========================

class ChatRequest(BaseModel):

    session_id: Optional[str] = None

    message: str

