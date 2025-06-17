from fastapi import Request, HTTPException
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
        raise HTTPException(status_code=401, detail="Invalid or expired token from leave_service check")
    return response.json()