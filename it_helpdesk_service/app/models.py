from pydantic import BaseModel
from typing import Optional

class TicketRequest(BaseModel):
    category: str
    priority: str
    description: str

class TicketStatus(BaseModel):
    status: str

class TicketResponse(BaseModel):
    ticket_id: str
    email: str
    category: str
    priority: str
    description: str
    status: str
    response: Optional[str] = None
