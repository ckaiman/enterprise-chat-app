from fastapi import Request, HTTPException, Depends
import requests
import os

AUTH_URL = os.getenv("AUTH_URL", "http://auth_service:8001/token/validate")

async def verify_token_dependency(request: Request):
    """Dependency to check for Authorization header and validate JWT with Auth Service"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    token = token.replace("Bearer ", "")
    response = requests.get(f"{AUTH_URL}?token={token}")

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token from committee_hearing_security_service check")
    
    user_data = response.json()
    return user_data

async def verify_security_admin_role(user_data: dict = Depends(verify_token_dependency)):
    """Dependency to check if the authenticated user has the 'security_admin' role."""
    role = user_data.get("role")
    if role != "security_admin":
        raise HTTPException(status_code=403, detail="User does not have security admin privileges")
    return user_data