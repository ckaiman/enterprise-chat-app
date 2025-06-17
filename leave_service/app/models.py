from pydantic import BaseModel

class LeaveBalanceResponse(BaseModel):
    annual: int
    sick: int