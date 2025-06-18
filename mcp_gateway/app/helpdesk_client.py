import requests
import os

HELPDESK_API_URL = os.getenv("HELPDESK_API_URL", "http://it_helpdesk_service:8003")
def submit_ticket(token: str, description: str, category: str = "other", priority: str = "medium"):
    """Submit an IT ticket"""
    headers = {"Authorization": f"Bearer {token}"}
    # The it_helpdesk_service should ideally derive the user from the token.
    # If email is still needed explicitly in the payload, it can be added here,
    # but it's often redundant if the service validates the token for user identity.
    payload = {
        "category": category,
        "priority": priority,
        "description": description
    }
    response = requests.post(f"{HELPDESK_API_URL}/tickets", headers=headers, json=payload)
    return response.json()