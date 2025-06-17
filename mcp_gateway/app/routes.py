from fastapi import APIRouter, Depends
from .auth_middleware import verify_token
from .leave_client import get_leave_balance, request_leave
from .helpdesk_client import submit_ticket

router = APIRouter()

@router.post("/chat")
async def chat(message: str, user=Depends(verify_token)):
    """Processes chat message and routes to backend tools."""
    email = user["sub"]

    if "leave balance" in message:
        return {"reply": get_leave_balance(email)}

    if "request leave" in message:
        return {"reply": request_leave(email, message)}

    if "help desk" in message or "IT issue" in message:
        return {"reply": submit_ticket(email, message)}

    return {"reply": "I didn't understand your request."}