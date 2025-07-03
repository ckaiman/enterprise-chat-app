from fastapi import APIRouter, Depends, HTTPException
from .auth_middleware import verify_token_dependency
from .mock_db import MOCK_LEAVE_BALANCES, MOCK_LEAVE_REQUESTS
from .models import LeaveBalanceResponse, LeaveRequest, LeaveRequestResponse
from datetime import date, timedelta
import uuid

router = APIRouter()

def calculate_business_days(start_date_str: str, end_date_str: str) -> int:
    """Calculates the number of business days (Mon-Fri) between two dates, inclusive."""
    try:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    except (ValueError, TypeError):
        # Return 0 if dates are invalid or None
        return 0

    if start_date > end_date:
        return 0

    business_days = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday is 0 and Sunday is 6
            business_days += 1
        current_date += timedelta(days=1)
    return business_days

@router.get("/leave/balance", response_model=LeaveBalanceResponse)
async def get_user_leave_balance(user_data: dict = Depends(verify_token_dependency)):
    user_email = user_data.get("sub") # 'sub' usually holds the email/username
    if not user_email:
        raise HTTPException(status_code=400, detail="User identifier not found in token")

    balance = MOCK_LEAVE_BALANCES.get(user_email)
    if balance is None:
        raise HTTPException(status_code=404, detail=f"Leave balance not found for user {user_email}")
    return LeaveBalanceResponse(**balance)

@router.post("/leave/request", response_model=LeaveRequestResponse)
async def submit_leave_request(request_data: LeaveRequest, user_data: dict = Depends(verify_token_dependency)):
    user_email = user_data.get("sub")
    if not user_email:
        raise HTTPException(status_code=400, detail="User identifier not found in token")

    if not all([request_data.leave_type, request_data.start_date, request_data.end_date]):
        raise HTTPException(status_code=400, detail="Missing required fields for leave request")

    # --- Balance Check Logic ---
    # 1. Get user's current balance
    user_balance = MOCK_LEAVE_BALANCES.get(user_email)
    if not user_balance:
        raise HTTPException(status_code=404, detail=f"Leave balance not found for user {user_email}")

    # 2. Calculate requested leave in hours
    leave_days = calculate_business_days(request_data.start_date, request_data.end_date)
    requested_hours = leave_days * 8  # Assuming 8-hour workdays

    # 3. Check against the correct leave type balance
    leave_type_to_check = request_data.leave_type.lower()
    if leave_type_to_check == "vacation":
        leave_type_to_check = "annual"
    
    available_balance = user_balance.get(leave_type_to_check)

    if available_balance is None:
        raise HTTPException(status_code=400, detail=f"Invalid leave type '{request_data.leave_type}' specified.")

    # 4. Compare and raise error if insufficient
    if requested_hours > available_balance:
        raise HTTPException(status_code=400, detail=f"Insufficient {leave_type_to_check} leave balance. Available: {available_balance}")

    new_request = {
        "request_id": str(uuid.uuid4()),
        "user_email": user_email,
        "leave_type": request_data.leave_type,
        "start_date": request_data.start_date,
        "end_date": request_data.end_date,
        "reason": request_data.reason,
        "status": "pending_approval" # Default status
    }
    MOCK_LEAVE_REQUESTS.append(new_request)
    
    return LeaveRequestResponse(**new_request)