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
import json # Import json for formatting data
import random # For varied responses

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

    data_payload = None # Initialize data payload
    if intent == "get_leave_balance":
        leave_type_query = entities.get("leave_type_query")
        balance_data = get_leave_balance(token, leave_type_query=leave_type_query)

        reply_text = "I couldn't retrieve your leave balance." # Default message
        if isinstance(balance_data, dict):
            if leave_type_query and leave_type_query.lower() != 'all':
                # User asked for a specific type like "vacation" or "sick"
                key_map = {'vacation': 'annual', 'annual': 'annual', 'sick': 'sick'}
                lookup_key = key_map.get(leave_type_query.lower())
                amount = balance_data.get(lookup_key)
                if amount is not None:
                    reply_text = f"I did a search of the leave request system and you have {amount} hours of {leave_type_query} leave available."
                    if amount < 10:
                        reply_text += f" Just a heads-up, you are getting a little low on {leave_type_query} leave."
                else:
                    # Fallback if the specific type wasn't in the response
                    annual = balance_data.get('annual', 0)
                    sick = balance_data.get('sick', 0)
                    reply_text = f"I couldn't find a specific balance for '{leave_type_query}', but your overall balances are: {annual} hours of annual leave and {sick} hours of sick leave."
            else:
                # General query for all balances
                annual = balance_data.get('annual', 0)
                sick = balance_data.get('sick', 0)
                base_reply = f"I did a search of the leave request system. You have {annual} hours of annual leave and {sick} hours of sick leave available."
                warnings = []
                if annual < 10:
                    warnings.append("annual leave")
                if sick < 10:
                    warnings.append("sick leave")

                if warnings:
                    low_on_str = " and ".join(warnings)
                    reply_text = f"{base_reply} Just a heads-up, you are getting a little low on {low_on_str}."
                else:
                    reply_text = base_reply
        elif isinstance(balance_data, str):
            reply_text = balance_data # Use the string response from the client if it's not a dict

        return {"reply": reply_text, "data": balance_data}
    elif intent == "request_leave":
        leave_response = request_leave(
            token=token,
            reason=entities.get("reason", user_message),
            leave_type=entities.get("leave_type"),
            start_date=entities.get("start_date"),
            end_date=entities.get("end_date"),
            hours=entities.get("hours")
        )
        if leave_response and leave_response.get("status") == "pending_approval":
             reply_text = f"Your leave request for {leave_response.get('leave_type', 'leave')} from {leave_response.get('start_date')} to {leave_response.get('end_date')} has been submitted for approval."
        elif leave_response and leave_response.get("error") == "insufficient_balance":
            leave_type = leave_response.get("leave_type", "leave")
            available = leave_response.get("available")
            
            sympathetic_responses = [
                f"I'm sorry, but it doesn't look like you have enough {leave_type} time available for this request.",
                f"Unfortunately, you don't have enough {leave_type} leave to cover that.",
                f"It seems your {leave_type} leave balance is too low for this request."
            ]
            reply_text = random.choice(sympathetic_responses)
            
            if available is not None:
                reply_text += f" You currently have {available} hours available."
        else:
             # Provide a more detailed error if possible
             reply_text = "There was an issue submitting your leave request. The service reported: " + leave_response.get('detail', 'Please try again or provide more details.')
        return {"reply": reply_text, "data": leave_response}
    elif intent == "submit_it_ticket":
        ticket_response = submit_ticket(
            token=token,
            description=entities.get("description", user_message),
            category=entities.get("category", "other"),
            priority=entities.get("priority", "medium")
        )
        if ticket_response and "ticket_id" in ticket_response:
            reply_text = f"I've submitted an IT ticket for you. The ticket ID is {ticket_response['ticket_id']}. A help desk specialist will be in touch."
        else:
            reply_text = "I was unable to submit your IT ticket. Please try again or contact the help desk directly."
        return {"reply": reply_text, "data": ticket_response}
    elif intent == "get_account_info":
        account_detail_query = entities.get("account_detail_query")
        details = get_account_details(token, account_detail_query=account_detail_query)
        
        reply_text = "I couldn't retrieve your account details."
        if isinstance(details, dict):
            name = details.get('name', 'N/A')
            email = details.get('email', 'N/A')
            role = details.get('role', 'N/A')
            reply_text = f"Here is your account information: Name: {name}, Email: {email}, Role: {role}."
        elif isinstance(details, str):
            reply_text = f"Your {account_detail_query} is: {details}."
        
        return {"reply": reply_text, "data": details}
    elif intent == "get_all_it_tickets":
        if user.get("role") == "it_admin":
            tickets = get_all_tickets(token)
            if tickets:
                reply_text = 'Here are all the open IT tickets.'
                return {"reply": reply_text, "data": tickets}
            else:
                return {"reply": "There are currently no open IT tickets.", "data": None}
        else:
            return {"reply": "Sorry, you do not have permission to view all IT tickets.", "data": None}
    elif intent == "submit_travel_security_request":
        response = submit_travel_security_request(
            token=token,
            details=entities.get("details", user_message),
            senator_name=entities.get("senator_name"),
            request_type=entities.get("request_type"),
            travel_type=entities.get("travel_type"),
            travel_type_other=entities.get("travel_type_other"),
            travel_date=entities.get("travel_date")
        )
        if response and "request_id" in response:
            reply_text = f"Your travel security request for {response.get('senator_name', 'the senator')} has been submitted. The request ID is {response['request_id']}."
        else:
            reply_text = "I was unable to submit your travel security request. Please provide more details or try again."
        return {"reply": reply_text, "data": response}
    elif intent == "submit_committee_hearing_security_request":
        response = submit_committee_hearing_security_request(
            token=token,
            committee_name=entities.get("committee_name", "Unknown Committee"),
            hearing_name=entities.get("hearing_name", "Unnamed Hearing"),
            location=entities.get("location", "Unknown Location"),
            description=entities.get("description", user_message),
            hearing_date=entities.get("hearing_date"),
            hearing_time=entities.get("hearing_time")
        )
        if response and "id" in response:
            committee_info = response.get('committee_hearing_data', {})
            committee_name = committee_info.get('committee_name', 'the')
            hearing_name = committee_info.get('name', 'hearing')
            reply_text = f"Your security request for the '{hearing_name}' ({committee_name} Committee) has been submitted."
        else:
            reply_text = "I was unable to submit the committee hearing security request. Please provide more details or try again."
        return {"reply": reply_text, "data": response}
    elif intent == "get_all_committee_hearing_security_requests":
        if user.get("role") == "security_admin":
            format_as_table = True
            requests_table = get_all_hearing_security_requests(
                token=token,
                committee_name_filter=entities.get("committee_name_filter"),
                location_filter=entities.get("location_filter"),
                level_filter=entities.get("level_filter"),
                start_date_filter=entities.get("start_date_filter"),
                end_date_filter=entities.get("end_date_filter"),
                limit=entities.get("limit"),
                format_as_table=format_as_table
            )
            if requests_table and "No requests found" not in str(requests_table):
                reply_text = f"Here are the committee hearing security requests matching your query:\n{requests_table}"
                return {"reply": reply_text, "data": None}
            else:
                return {"reply": "No committee hearing security requests were found matching your criteria.", "data": None}
        else:
            return {"reply": "Sorry, you do not have permission to view all committee hearing security requests.", "data": None}
    elif intent == "get_most_recent_committee_hearing_security_request":
        if user.get("role") == "security_admin":
            format_as_table = True
            request_table = get_most_recent_hearing_security_request(token, format_as_table=format_as_table)
            if request_table and "No requests found" not in str(request_table):
                reply_text = f"Here is the most recent committee hearing security request:\n{request_table}"
                return {"reply": reply_text, "data": None}
            else:
                return {"reply": "No committee hearing security requests were found.", "data": None}
        else:
            return {"reply": "Sorry, you do not have permission to view the most recent committee hearing security request.", "data": None}
    else: # Default if intent is "unknown" or not handled
        return {"reply": "I'm sorry, I didn't understand that. Could you please rephrase your request?", "data": None}