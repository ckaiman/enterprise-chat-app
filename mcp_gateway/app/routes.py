from fastapi import APIRouter, Depends
# Add Pydantic BaseModel for request body validation
from pydantic import BaseModel
from .auth_middleware import verify_token, get_raw_token
from .leave_client import get_leave_balance, request_leave
from .helpdesk_client import submit_ticket

router = APIRouter()

# Define a Pydantic model for the chat request body
class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
# Modify the endpoint to expect the ChatRequest model
async def chat(request_data: ChatRequest, user=Depends(verify_token), token: str = Depends(get_raw_token)):
    """Processes chat message and routes to backend tools."""
    email = user["sub"]
    # Convert to lowercase and strip whitespace for more robust matching
    message_content = request_data.message.lower().strip()

    # More flexible check for leave balance
    if "leave" in message_content and "balance" in message_content:
        return {"reply": get_leave_balance(token)}
    elif "request leave" in message_content: # Changed to elif
        return {"reply": request_leave(token, message_content)}
    elif "help desk" in message_content or "IT issue" in message_content: # Changed to elif
        return {"reply": submit_ticket(token, request_data.message)}
    else: # Added else for clarity
        return {"reply": "I didn't understand your request."}