import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expires after 1 hour

MOCK_USERS = {
    "alice@example.com": {"name": "Alice Johnson", "password": "hashedpassword123", "role": "employee"},
    "bob@example.com": {"name": "Bob Smith", "password": "hashedpassword456", "role": "it_admin"},
    "security_admin@example.com": {"name": "Security Admin", "password": "securepassword789", "role": "security_admin"} # New user
}

# CORS Origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")