from fastapi import APIRouter, Depends, HTTPException
from .models import TicketRequest, TicketStatus, TicketResponse # Import TicketResponse
from .mock_db import mock_tickets, mock_categories
from .auth_middleware import verify_token_dependency # Changed import
import uuid


router = APIRouter()

@router.get("/tickets")
async def get_ticket_history(user=Depends(verify_token_dependency)): # Changed dependency
    """Return user's ticket history"""
    email = user["sub"]
    # Use .get() for safer access in case a ticket dict is malformed
    history = [ticket for ticket in mock_tickets if ticket.get("email") == email]
    return {"email": email, "tickets": history}

@router.get("/categories")
async def get_ticket_categories():
    """Return available IT issue categories"""
    return {"categories": mock_categories}

@router.post("/tickets", response_model=TicketResponse) # Changed response_model
async def submit_ticket(request: TicketRequest, user=Depends(verify_token_dependency)): # Changed dependency
    """Submit a new IT help desk ticket"""
    email = user["sub"]

    ticket = {
        "ticket_id": str(uuid.uuid4()),
        "email": email,
        "category": request.category,
        "priority": request.priority,
        "description": request.description,
        "status": "open",
        "response": None
    }
    
    mock_tickets.append(ticket)
    return ticket