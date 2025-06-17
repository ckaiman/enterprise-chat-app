from fastapi import FastAPI, APIRouter, Depends, HTTPException
from .models import LeaveRequest, LeaveBalance, LeaveHistory
from .mock_db import mock_balances, mock_requests
from .routes import router
from .auth_middleware import verify_token

app = FastAPI(title="Leave Request API")
router = APIRouter()

@router.get("/leave/balance", response_model=LeaveBalance)
async def get_leave_balance(user=Depends(verify_token)):
    """Return user's leave balances"""
    email = user["sub"]
    balance = mock_balances.get(email)
    if not balance:
        raise HTTPException(status_code=404, detail="No leave data found")
    return {"email": email, **balance}

@router.get("/leave/history", response_model=LeaveHistory)
async def get_leave_history(user=Depends(verify_token)):
    """Return user's leave request history"""
    email = user["sub"]
    history = [req for req in mock_requests if req["email"] == email]
    return {"email": email, "history": history}

@router.post("/leave/request")
async def request_leave(request: LeaveRequest, user=Depends(verify_token)):
    """Submit a new leave request"""
    email = user["sub"]
    if email != request.email:
        raise HTTPException(status_code=403, detail="Unauthorized request")

    mock_requests.append(request.dict())
    return {"message": "Leave request submitted"}