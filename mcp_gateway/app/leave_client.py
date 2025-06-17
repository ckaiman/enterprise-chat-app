import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LEAVE_API_URL = os.getenv("LEAVE_API_URL", "http://leave_service:8002")

def get_leave_balance(token: str):
    """Fetch user leave balance"""
    logger.info(f"Fetching leave balance for token (first 10 chars): {token[:10]}...")
    response = requests.get(f"{LEAVE_API_URL}/leave/balance", headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    logger.info(f"Leave balance response for token {token[:10]}...: {response_data}")
    return response_data

def request_leave(token: str, message: str):
    """Submit a leave request"""
    logger.info(f"Requesting leave for token (first 10 chars): {token[:10]}... with message: {message}")
    # Adjust payload as necessary based on what leave_service expects
    payload = {"leave_details_from_message": message, "leave_type": "vacation", "start_date": "2025-06-20", "end_date": "2025-06-21"}
    response = requests.post(f"{LEAVE_API_URL}/leave/request", headers={"Authorization": f"Bearer {token}"}, json=payload)
    response_data = response.json()
    logger.info(f"Leave request response for token {token[:10]}...: {response_data}")
    return response_data