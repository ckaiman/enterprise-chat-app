from fastapi import APIRouter, Depends, HTTPException
from .auth_middleware import verify_token_dependency
from .mock_db import MOCK_LEAVE_BALANCES
from .models import LeaveBalanceResponse

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