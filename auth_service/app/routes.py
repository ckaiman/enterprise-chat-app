from fastapi import APIRouter, HTTPException, Depends
from .models import LoginRequest, TokenResponse
from .utils import create_access_token, verify_token
from .config import MOCK_USERS

router = APIRouter()

@router.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest):
    """Validate user credentials and return a JWT token"""
    user = MOCK_USERS.get(request.email)
    if not user or request.password != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": request.email, "name": user["name"], "role": user["role"]}
    token = create_access_token(token_data)

    return {"access_token": token}

@router.get("/token/validate")
def validate_token(token: str):
    """Verify JWT and return user identity"""
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_data