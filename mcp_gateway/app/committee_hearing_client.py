import requests
import os
import logging
from typing import Optional, List, Dict

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

def format_hearing_requests_as_table(requests: List[Dict]) -> str:
    """Formats a list of committee hearing security requests as an HTML table."""
    if not requests:
        return "No hearing security requests found."

    # Basic styling for the table
    html = '<table style="width:100%; border-collapse: collapse; border: 1px solid #ddd; font-family: sans-serif; font-size: 0.9em;">'
    # Table header
    html += '<tr style="background-color: #f2f2f2;">'
    html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">ID</th>'
    html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Committee</th>'
    html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Name</th>'
    html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Location</th>'
    html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Date</th>'
    html += '<th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Description</th>'
    html += '</tr>'

    # Table rows
    for req in requests:
        committee_data = req.get("committee_hearing_data", {})
        # Get date part only and handle potential None values
        incident_date_str = req.get("datetime_incident", "N/A")
        incident_date = incident_date_str.split('T')[0] if incident_date_str and incident_date_str != "N/A" else "N/A"

        html += '<tr>'
        html += f'<td style="padding: 8px; border: 1px solid #ddd;">{req.get("id", "N/A")}</td>'
        html += f'<td style="padding: 8px; border: 1px solid #ddd;">{committee_data.get("committee_name", "N/A")}</td>'
        html += f'<td style="padding: 8px; border: 1px solid #ddd;">{committee_data.get("name", "N/A")}</td>'
        html += f'<td style="padding: 8px; border: 1px solid #ddd;">{committee_data.get("location", "N/A")}</td>'
        html += f'<td style="padding: 8px; border: 1px solid #ddd;">{incident_date}</td>'
        html += f'<td style="padding: 8px; border: 1px solid #ddd;">{req.get("description", "N/A")}</td>'
        html += '</tr>'

    html += '</table>'
    return html

def get_all_hearing_security_requests(
    token: str,
    committee_name_filter: Optional[str] = None,
    location_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    start_date_filter: Optional[str] = None,
    end_date_filter: Optional[str] = None,
    format_as_table: bool = False
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
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {endpoint} failed: {e}")
        return f"Error: Could not retrieve hearing security requests. {e}"
    
    if format_as_table:
        return format_hearing_requests_as_table(data)
    return data

def get_most_recent_hearing_security_request(token: str, format_as_table: bool = False):
    """Fetch the most recent committee hearing security request (requires security_admin privileges)"""
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{COMMITTEE_HEARING_API_URL}/hearings/security/most-recent"
    logger.info(f"Fetching the most recent committee hearing security request from {endpoint}")
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request to {endpoint} failed: {e}")
        return f"Error: Could not retrieve the most recent hearing security request. {e}"
    
    if format_as_table and data:
        return format_hearing_requests_as_table([data])
    return data