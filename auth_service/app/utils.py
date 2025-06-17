from datetime import datetime, timedelta
from jose import JWTError, jwt
from .config import SECRET_KEY, ALGORITHM

def create_access_token(data: dict):
    """Generates a JWT token with user data"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    """Decodes JWT and returns user data if valid"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None