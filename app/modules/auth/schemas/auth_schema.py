
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

    guest_token: Optional[str] = None


# =========================
# LOGIN
# =========================

class LoginRequest(BaseModel):

    email: EmailStr

    password: str

    guest_token: Optional[str] = None


# =========================
# TOKEN RESPONSE
# =========================

class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str

    user: dict | None = None


# =========================
# REFRESH TOKEN REQUEST / RESPONSE
# =========================

class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):

    access_token: str

    token_type: str


# =========================
# LOGOUT REQUEST
# =========================

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


# =========================
# CHAT REQUEST
# =========================

class ChatRequest(BaseModel):

    session_id: Optional[str] = None

    message: str


# =========================
# GOOGLE AUTH
# =========================

class GoogleAuthRequest(BaseModel):

    credential: str

    guest_token: Optional[str] = None

