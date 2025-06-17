import requests
import os

LEAVE_API_URL = os.getenv("LEAVE_API_URL", "http://leave_service:8002")

def get_leave_balance(email: str):
    """Fetch user leave balance"""
    response = requests.get(f"{LEAVE_API_URL}/leave/balance", headers={"Authorization": f"Bearer {email}"})
    return response.json()

def request_leave(email: str, message: str):
    """Submit a leave request"""
    response = requests.post(f"{LEAVE_API_URL}/leave/request", json={"email": email, "leave_type": "vacation", "start_date": "2025-06-20", "end_date": "2025-06-21"})
    return response.json()