from fastapi import APIRouter, Depends
# Add Pydantic BaseModel for request body validation
from pydantic import BaseModel
from .auth_middleware import verify_token
from .leave_client import get_leave_balance, request_leave
from .helpdesk_client import submit_ticket

router = APIRouter()

# Define a Pydantic model for the chat request body
class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
# Modify the endpoint to expect the ChatRequest model
async def chat(request_data: ChatRequest, user=Depends(verify_token)):
    """Processes chat message and routes to backend tools."""
    email = user["sub"]
    message_content = request_data.message.lower() # Convert to lowercase for case-insensitive matching

    # More flexible check for leave balance
    if "leave" in message_content and "balance" in message_content:
        return {"reply": get_leave_balance(email)}

    if "request leave" in message_content:
        return {"reply": request_leave(email, message_content)}

    if "help desk" in message_content or "IT issue" in message_content:
        return {"reply": submit_ticket(email, request_data.message)} # Pass original message if needed by submit_ticket

    return {"reply": "I didn't understand your request."}