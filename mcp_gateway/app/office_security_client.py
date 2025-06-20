import requests
import os
import logging

logger = logging.getLogger(__name__)

OFFICE_SECURITY_API_URL = os.getenv("OFFICE_SECURITY_API_URL", "http://office_security_service:8004")

def submit_travel_security_request(token: str, details: str, senator_name: str = None, request_type: str = None, travel_type: str = None, travel_type_other: str = None, travel_date: str = None):
    """
    Submits a travel security request to the office_security_service.
    """
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "senator_name": senator_name,
        "request_type": request_type,
        "travel_type": travel_type,
        "travel_type_other": travel_type_other,
        "travel_date": travel_date,
        "details": details
    }
    endpoint = f"{OFFICE_SECURITY_API_URL}/security/travel-requests"
    logger.info(f"Submitting travel security request to {endpoint} with payload: {payload}")
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        return response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from {endpoint}. Response text: {response.text}")
        return {"error": "Received invalid response from office security service", "status_code": response.status_code, "details": response.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {endpoint} failed: {e}")
        return {"error": f"Request to office security service failed: {e}"}