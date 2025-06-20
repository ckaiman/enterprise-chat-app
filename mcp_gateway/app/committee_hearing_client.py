import requests
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

COMMITTEE_HEARING_API_URL = os.getenv("COMMITTEE_HEARING_API_URL", "http://committee_hearing_security_service:8005")

def submit_committee_hearing_security_request(
    token: str, 
    committee_name: str,
    hearing_name: str,
    location: str,
    description: Optional[str] = None,
    hearing_date: Optional[str] = None, # Expected YYYY-MM-DD
    hearing_time: Optional[str] = None  # Expected HH:MM
):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "committee_hearing_data": {
            "name": hearing_name,
            "location": location,
            "committee_name": committee_name
        },
        "description": description,
        "datetime_incident": f"{hearing_date}T{hearing_time}:00" if hearing_date and hearing_time else None # Combine date and time
    }
    endpoint = f"{COMMITTEE_HEARING_API_URL}/hearings/security" # Matches the prefix and path in committee_hearing_security_service
    logger.info(f"Submitting committee hearing security request to {endpoint} with payload: {payload}")
    response = requests.post(endpoint, headers=headers, json=payload)
    return response.json()

def get_all_hearing_security_requests(
    token: str,
    committee_name_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    start_date_filter: Optional[str] = None,
    end_date_filter: Optional[str] = None
):
    """Fetch all committee hearing security requests (requires security_admin privileges)"""
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{COMMITTEE_HEARING_API_URL}/hearings/security/all" # Matches the path in committee_hearing_security_service
    
    params = {}
    if committee_name_filter:
        params["committeeNameFilter"] = committee_name_filter
    if location_filter:
        params["locationFilter"] = location_filter
    if level_filter:
        params["levelFilter"] = level_filter
    if start_date_filter:
        params["startDateFilter"] = start_date_filter
    if end_date_filter:
        params["endDateFilter"] = end_date_filter

    logger.info(f"Fetching committee hearing security requests from {endpoint} with params: {params}")
    response = requests.get(endpoint, headers=headers, params=params)
    return response.json()

def get_most_recent_hearing_security_request(token: str):
    """Fetch the most recent committee hearing security request (requires security_admin privileges)"""
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{COMMITTEE_HEARING_API_URL}/hearings/security/most-recent"
    logger.info(f"Fetching the most recent committee hearing security request from {endpoint}")
    response = requests.get(endpoint, headers=headers)
    return response.json()