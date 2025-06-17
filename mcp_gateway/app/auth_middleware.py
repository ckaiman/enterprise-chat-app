from fastapi import Request, HTTPException
import requests
import os

AUTH_URL = os.getenv("AUTH_URL", "http://auth_service:8001/token/validate")

async def verify_token(request: Request):
    """Check for Authorization header and validate JWT with Auth Service"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    token = token.replace("Bearer ", "")
    response = requests.get(f"{AUTH_URL}?token={token}")

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return response.json()  # Returns user identity (email, role)

async def get_raw_token(request: Request):
    """Extracts the raw token string from the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format, must be Bearer token")
    return auth_header.split("Bearer ")[1]