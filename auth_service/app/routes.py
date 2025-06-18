from fastapi import APIRouter, HTTPException, Depends, Request
from .models import LoginRequest, TokenResponse, UserInfoResponse # Assuming UserInfoResponse is added to models.py
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

async def get_current_user_data_from_header(request: Request):
    """
    Dependency to extract token from Authorization header and verify it.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    parts = auth_header.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid token format, must be Bearer token")
    
    token_str = parts[1]
    user_data = verify_token(token_str) # Call the utility function
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token (from header check)")
    return user_data

@router.get("/account/me", response_model=UserInfoResponse)
def get_my_account_info(user_data: dict = Depends(get_current_user_data_from_header)):
    """Return information about the authenticated user"""
    return UserInfoResponse(email=user_data.get("sub"), name=user_data.get("name"), role=user_data.get("role"))