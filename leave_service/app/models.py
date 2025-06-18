from pydantic import BaseModel
from typing import Optional

class LeaveBalanceResponse(BaseModel):
    annual: int
    sick: int

class LeaveRequest(BaseModel):
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None

class LeaveRequestResponse(BaseModel):
    request_id: str
    user_email: str
    leave_type: str
    start_date: str
    end_date: str
    reason: Optional[str] = None
    status: str