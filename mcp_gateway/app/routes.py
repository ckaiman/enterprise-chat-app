from fastapi import APIRouter, Depends
# Add Pydantic BaseModel for request body validation
from pydantic import BaseModel
from .auth_middleware import verify_token, get_raw_token
from .leave_client import get_leave_balance, request_leave
from .helpdesk_client import submit_ticket, get_all_tickets
from .llm_client import get_intent_and_entities # Import the LLM client function
from .account_client import get_account_details # Import the new account client function
from .office_security_client import submit_travel_security_request
from .committee_hearing_client import submit_committee_hearing_security_request, get_all_hearing_security_requests, get_most_recent_hearing_security_request
import logging # Import the logging module

router = APIRouter()

# Define a Pydantic model for the chat request body
class ChatRequest(BaseModel):
    message: str

# Get a logger instance
logger = logging.getLogger(__name__)

@router.post("/chat")
# Modify the endpoint to expect the ChatRequest model
async def chat(request_data: ChatRequest, user=Depends(verify_token), token: str = Depends(get_raw_token)):
    """Processes chat message and routes to backend tools."""
    user_message = request_data.message

    # Get intent and entities from the LLM client
    llm_response = get_intent_and_entities(user_message)
    intent = llm_response.get("intent")
    entities = llm_response.get("entities", {})

    # Log the intent and entities received from the LLM client
    logger.info(f"MCP Gateway - Intent: {intent}, Entities: {entities}")

    if intent == "get_leave_balance":
        leave_type_query = entities.get("leave_type_query")
        return {"reply": get_leave_balance(token, leave_type_query=leave_type_query)}
    elif intent == "request_leave":
        # Pass original message or extracted entities.
        # For this example, leave_client.request_leave might need to be updated
        # to accept more detailed entities if the LLM provides them (e.g., dates).
        return {"reply": request_leave(token, user_message)} # Or request_leave(token, **entities)
    elif intent == "submit_it_ticket":
        return {"reply": submit_ticket(
            token=token,
            description=entities.get("description", user_message),
            category=entities.get("category", "other"), # Default if not extracted
            priority=entities.get("priority", "medium")  # Default if not extracted
        )}
    elif intent == "get_account_info":
        account_detail_query = entities.get("account_detail_query")
        return {"reply": get_account_details(token, account_detail_query=account_detail_query)}
    elif intent == "get_all_it_tickets":
        # Check user role before calling the client
        if user.get("role") == "it_admin":
            return {"reply": get_all_tickets(token)}
        else:
            return {"reply": "Sorry, you do not have permission to view all IT tickets."}
    elif intent == "submit_travel_security_request":
        return {"reply": submit_travel_security_request(
            token=token,
            details=entities.get("details", user_message), # Fallback to full message
            senator_name=entities.get("senator_name"),
            request_type=entities.get("request_type"),
            travel_type=entities.get("travel_type"),
            travel_type_other=entities.get("travel_type_other"),
            travel_date=entities.get("travel_date")
        )}
    elif intent == "submit_committee_hearing_security_request":
        return {"reply": submit_committee_hearing_security_request(
            token=token,
            committee_name=entities.get("committee_name", "Unknown Committee"),
            hearing_name=entities.get("hearing_name", "Unnamed Hearing"),
            location=entities.get("location", "Unknown Location"),
            description=entities.get("description", user_message), # Fallback to full message
            hearing_date=entities.get("hearing_date"),
            hearing_time=entities.get("hearing_time")
        )}
    elif intent == "get_all_committee_hearing_security_requests":
        # Check user role before calling the client
        if user.get("role") == "security_admin":
            # Default to a table format for a better user experience in the chat.
            format_as_table = True
            return {"reply": get_all_hearing_security_requests(
                token=token,
                committee_name_filter=entities.get("committee_name_filter"),
                location_filter=entities.get("location_filter"),
                level_filter=entities.get("level_filter"),
                start_date_filter=entities.get("start_date_filter"),
                end_date_filter=entities.get("end_date_filter"),
                format_as_table=format_as_table
            )}
        else:
            return {"reply": "Sorry, you do not have permission to view all committee hearing security requests."}
    elif intent == "get_most_recent_committee_hearing_security_request":
        if user.get("role") == "security_admin":
            # Default to a table format for a better user experience in the chat.
            format_as_table = True
            return {"reply": get_most_recent_hearing_security_request(token, format_as_table=format_as_table)}
        else:
            return {"reply": "Sorry, you do not have permission to view the most recent committee hearing security request."}
    else: # Default if intent is "unknown" or not handled
        return {"reply": "I didn't understand your request."}