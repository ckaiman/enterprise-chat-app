import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_URL_BASE", "http://auth_service:8001") # Assuming AUTH_URL points to validate, so create a base

def get_account_details(token: str, account_detail_query: str = None):
    """Fetch authenticated user's account details from auth_service"""
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{AUTH_SERVICE_URL}/account/me"
    logger.info(f"Fetching account details for token (first 10 chars): {token[:10]}..., specific detail: {account_detail_query} from {endpoint}")
    response = requests.get(endpoint, headers=headers)
    response_data = response.json()
    logger.info(f"Full account details response from service for token {token[:10]}...: {response_data}")

    if not account_detail_query or account_detail_query.lower() == "all":
        return response_data # Return the full object

    query_lower = account_detail_query.lower()
    if query_lower == "email":
        return {"email": response_data.get("email", "Not available")}
    elif query_lower == "name":
        return {"name": response_data.get("name", "Not available")}
    elif query_lower == "role":
        return {"role": response_data.get("role", "Not available")}
    else: # Unknown specific detail requested
        return f"I found your account details: {response_data}. Which specific piece of information were you interested in?"

    # Fallback, should not be reached if logic above is complete
    return response_data