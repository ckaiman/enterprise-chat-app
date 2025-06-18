from fastapi import APIRouter, Depends, HTTPException
from .auth_middleware import verify_token_dependency
from .mock_db import MOCK_LEAVE_BALANCES, MOCK_LEAVE_REQUESTS
from .models import LeaveBalanceResponse, LeaveRequest, LeaveRequestResponse
import uuid

router = APIRouter()

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

    # Basic validation (in a real app, this would be more robust, checking dates, balances, etc.)
    if not all([request_data.leave_type, request_data.start_date, request_data.end_date]):
        raise HTTPException(status_code=400, detail="Missing required fields for leave request")

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