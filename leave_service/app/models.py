from pydantic import BaseModel
from typing import Optional

class LeaveRequest(BaseModel):
    email: str
    leave_type: str  # "vacation", "sick", "personal"
    start_date: str
    end_date: str
    reason: Optional[str] = None

class LeaveBalance(BaseModel):
    email: str
    vacation_days: int
    sick_days: int
    personal_days: int

class LeaveHistory(BaseModel):
    email: str
    history: list