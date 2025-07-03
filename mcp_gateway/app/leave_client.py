import requests
import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LEAVE_API_URL = os.getenv("LEAVE_API_URL", "http://leave_service:8002")

def get_leave_balance(token: str, leave_type_query: str = None):
    """Fetch user leave balance"""
    logger.info(f"Fetching leave balance for token (first 10 chars): {token[:10]}..., specific type: {leave_type_query}")
    response = requests.get(f"{LEAVE_API_URL}/leave/balance", headers={"Authorization": f"Bearer {token}"})
    response_data = response.json()
    logger.info(f"Full leave balance response from service for token {token[:10]}...: {response_data}")

    if not leave_type_query or leave_type_query.lower() == "all":
        return response_data # Return the full object

    # Normalize query
    query_lower = leave_type_query.lower()
    if query_lower in ["annual", "vacation"]: # Treat "vacation" as "annual" for lookup
        key_to_check = "annual"
    elif query_lower == "sick":
        key_to_check = "sick"
    else: # Unknown specific type requested, return full object or a specific message
        return f"I found your balances: {response_data}. Which specific type were you interested in?"

    return {key_to_check: response_data.get(key_to_check, "Not available")}

def request_leave(token: str, reason: str, leave_type: str = None, start_date: str = None, end_date: str = None):
    """Submit a leave request"""
    logger.info(f"Requesting leave for token (first 10 chars): {token[:10]}... Details: type={leave_type}, start={start_date}, end={end_date}, reason='{reason}'")
    
    # This payload should match what the leave_service /leave/request endpoint expects.
    # We only include keys if they have a value.
    payload = { "reason": reason }
    if leave_type:
        payload["leave_type"] = leave_type
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    response = requests.post(f"{LEAVE_API_URL}/leave/request", headers={"Authorization": f"Bearer {token}"}, json=payload)

    # If the request fails (e.g., 400 Bad Request), the service might provide a reason.
    if not response.ok:
        try:
            error_data = response.json()
            logger.warning(f"Leave request failed for token {token[:10]}... with status {response.status_code}: {error_data}")
            # Check for a specific "insufficient balance" message from the service
            detail = error_data.get("detail", "").lower()
            if "insufficient" in detail and "balance" in detail:
                # Attempt to parse a structured error from the detail string
                # e.g., "Insufficient annual leave balance. Available: 8"
                available_match = re.search(r'available: (\d+\.?\d*)', detail)
                available = float(available_match.group(1)) if available_match else None
                
                leave_type_match = re.search(r'insufficient (\w+) leave', detail)
                leave_type_from_error = leave_type_match.group(1) if leave_type_match else leave_type or "leave"
                
                return {"error": "insufficient_balance", "leave_type": leave_type_from_error, "available": available}
            return error_data # Return the original error if it's not about balance
        except requests.exceptions.JSONDecodeError:
            logger.error(f"Leave request failed for token {token[:10]}... with status {response.status_code} and non-JSON response.")
            return {"error": "service_error", "message": "The leave service returned an unexpected error."}

    # If the request is successful
    response_data = response.json()
    logger.info(f"Leave request response for token {token[:10]}...: {response_data}")
    return response_data