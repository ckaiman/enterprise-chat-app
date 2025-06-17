from pydantic import BaseModel
from typing import Optional

class TicketRequest(BaseModel):
    email: str
    category: str  # "hardware", "software", "network", "other"
    priority: str  # "low", "medium", "high"
    description: str

class TicketStatus(BaseModel):
    ticket_id: str
    email: str
    status: str  # "open", "in progress", "resolved"
    response: Optional[str] = None