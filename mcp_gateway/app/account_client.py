import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_URL_BASE", "http://auth_service:8001") # Assuming AUTH_URL points to validate, so create a base

def get_account_details(token: str):
    """Fetch authenticated user's account details from auth_service"""
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{AUTH_SERVICE_URL}/account/me"
    logger.info(f"Fetching account details for token (first 10 chars): {token[:10]}... from {endpoint}")
    response = requests.get(endpoint, headers=headers)
    response_data = response.json()
    logger.info(f"Account details response for token {token[:10]}...: {response_data}")
    return response_data