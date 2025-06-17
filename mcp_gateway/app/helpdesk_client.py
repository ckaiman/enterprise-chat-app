import requests
import os

HELPDESK_API_URL = os.getenv("HELPDESK_API_URL", "http://it_helpdesk_service:8003")

def submit_ticket(email: str, message: str):
    """Submit an IT ticket"""
    response = requests.post(f"{HELPDESK_API_URL}/tickets", json={"email": email, "category": "hardware", "priority": "high", "description": message})
    return response.json()