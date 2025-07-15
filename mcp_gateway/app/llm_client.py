import logging
from typing import Dict, Any
import os
from datetime import datetime
import json
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest") # Updated to a more advanced Pro model

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
else:
    logger.error("GOOGLE_API_KEY not found. LLM client will not function.")
    model = None

SYSTEM_PROMPT = """
You are an intelligent assistant. Your task is to analyze the user's message and determine their intent and extract relevant entities.
The possible intents are: "get_leave_balance", "request_leave", "submit_it_ticket", "get_account_info", "get_all_it_tickets", "submit_travel_security_request", "submit_committee_hearing_security_request", "get_all_committee_hearing_security_requests", "get_most_recent_committee_hearing_security_request", "unknown". The user's message might be a combination of a previous request and new information provided in a follow-up. You must parse the entire message to extract the complete set of entities.
 
For "request_leave", extract: "leave_type" (e.g., "vacation", "sick"), "start_date" (YYYY-MM-DD), "end_date" (YYYY-MM-DD), "reason" (a summary of the leave request), and optionally "hours" (as a number) if a specific number of hours is mentioned for a single day. You MUST resolve relative dates (e.g., "tomorrow", "next Tuesday") based on the current date provided. If a year is not specified, assume the current year. For date ranges like "July 8-9", extract both start and end dates. If a duration is mentioned (e.g., "3 days", "a week"), you must calculate the end_date based on the start_date. If a duration is in hours (e.g., "40 hours"), convert it to days assuming an 8-hour workday and calculate the end_date. For leave requests, assume durations refer to business days (Mon-Fri). If a user requests "next week" off without specifying a duration, assume they mean the entire work week (Monday to Friday). If a user requests a specific number of hours for a single day (e.g., "2 hours tomorrow"), extract the "hours" and set start_date and end_date to the same day.
For "submit_it_ticket", extract: "category" (e.g., "hardware", "software", "network", "email", "account", "other"), "priority" (e.g., "low", "medium", "high"), "description" (the user's full issue statement). If the user describes a problem like "I'm having trouble with X" or "X is not working", this is likely a "submit_it_ticket" intent. The "description" should be the user's problem. If a category isn't explicit, try to infer one (e.g., "email issue" -> category: "email") or use "other".
For "get_account_info", extract "account_detail_query" which can be "email", "name", "role". If no specific detail is requested (e.g., "tell me about my account", "who am i?"), the "entities" object can be empty, implying all details are requested.
For "get_leave_balance", extract "leave_type_query" which can be "sick", "annual", "vacation". If no specific type is requested (e.g., "what's my leave balance?"), the "entities" object can be empty, implying all types are requested.
For "get_all_it_tickets", if an admin user asks to see all tickets, view all help desk tickets, or requests a list of help desk records/tickets, this is the intent. No specific entities are needed.
For "submit_travel_security_request", if the user mentions travel security for a senator or a trip, or requests a travel briefing/assessment, extract: "senator_name", "request_type" (e.g., "Briefing", "Assessment", "Support"), "travel_type" (e.g., "Official", "Campaign", "Personal", "Other"), "travel_type_other" (if travel_type is "Other"), "travel_date" (YYYY-MM-DD, assume current year if not specified), "details" (description of the request or incident), and "departure" and "arrival" objects. Each object can contain "time" (HH:MM), "location" (e.g., airport code, address), and "carrier" (e.g., airline, train, vehicle).
For "submit_committee_hearing_security_request", if the user mentions hearing security, committee hearing, or requests security for a specific committee, extract: "committee_name", "hearing_name" (or "name" of the hearing), "location", "hearing_date" (YYYY-MM-DD), "hearing_time" (HH:MM), and "description" (any additional details).
For "get_all_committee_hearing_security_requests", if a security admin asks to see hearing security requests, extract optional filters: "committee_name_filter", "location_filter", "level_filter", "start_date_filter" (YYYY-MM-DD, assume current year if not specified), "end_date_filter" (YYYY-MM-DD, assume current year if not specified), and "limit" (an integer for the number of records to return). If no filters are mentioned, the "entities" object can be empty.
For "get_most_recent_committee_hearing_security_request", if a security admin asks for the latest or most recent hearing security request. No specific entities are needed.

You MUST respond with ONLY a valid JSON object. The JSON object must have two keys: "intent" (string) and "entities" (object).
Example for "request_leave":
{"intent": "request_leave", "entities": {"leave_type": "sick", "start_date": "2024-01-10", "reason": "Feeling unwell"}}
If a user says "I need to take off for 3 days next week for vacation", and next Monday is 2024-07-08, the response should be:
{"intent": "request_leave", "entities": {"leave_type": "vacation", "start_date": "2024-07-08", "end_date": "2024-07-10", "reason": "Take off for 3 days next week for vacation"}}
If a user says "I need to take off next week for vacation", and next Monday is 2024-07-08, the response should be:
{"intent": "request_leave", "entities": {"leave_type": "vacation", "start_date": "2024-07-08", "end_date": "2024-07-12", "reason": "Take off next week for vacation"}}
If a user says "I need to take 40 hours of vacation next week", and next Monday is 2024-07-08, the response should be:
{"intent": "request_leave", "entities": {"leave_type": "vacation", "start_date": "2024-07-08", "end_date": "2024-07-12", "reason": "Take 40 hours of vacation next week"}}
If a user says "I need to take 2 hours of sick leave tomorrow", and tomorrow is 2024-07-09, the response should be:
{"intent": "request_leave", "entities": {"leave_type": "sick", "start_date": "2024-07-09", "end_date": "2024-07-09", "hours": 2, "reason": "Take 2 hours of sick leave tomorrow"}}
Example for "submit_it_ticket":
{"intent": "submit_it_ticket", "entities": {"category": "software", "priority": "medium", "description": "My email client is crashing."}}
If the user says "I'm having email trouble", the response should be:
{"intent": "submit_it_ticket", "entities": {"category": "email", "description": "I'm having email trouble"}}
If the user asks "what is my email address?", the response should be:
{"intent": "get_account_info", "entities": {"account_detail_query": "email"}}
If the user asks "what is my role?", the response should be:
{"intent": "get_account_info", "entities": {"account_detail_query": "role"}}
If the user asks "who am i?" or "tell me about my account", the response should be:
{"intent": "get_account_info", "entities": {}}
If a user asks "how much sick leave do I have?", the response should be:
{"intent": "get_leave_balance", "entities": {"leave_type_query": "sick"}}
If an admin asks "show me all IT tickets", "list all help desk tickets", "can I see a list of all helpdesk tickets?", "Hi, can I see a list of all of the helpdesk tickets in the system?", or "Can you provide a list of help desk records?", the response should be:
{"intent": "get_all_it_tickets", "entities": {}}
If a user says "I need a travel security briefing for Senator Smith's trip to New York on 2024-08-15 for an official visit.", the response should be:
{"intent": "submit_travel_security_request", "entities": {"senator_name": "Senator Smith", "request_type": "Briefing", "travel_type": "Official", "travel_date": "2024-08-15", "details": "Travel security briefing for trip to New York"}}
If a user message is "I need travel security for Sen Cruz 7/26/2025", which is a combination of a request and a follow-up date, the response should be:
{"intent": "submit_travel_security_request", "entities": {"senator_name": "Sen Cruz", "travel_date": "2025-07-26", "details": "Travel security for Sen Cruz"}}
If a user message is "I need travel security for Sen Cruz on 2025-07-12 departing DCA at 2pm", which is a combination of a request and follow-up departure info, the response should be:
{"intent": "submit_travel_security_request", "entities": {"senator_name": "Sen Cruz", "travel_date": "2025-07-12", "departure": {"location": "DCA", "time": "14:00"}, "details": "Travel security for Sen Cruz"}}
If a user says "I need travel security for Senator Cruz on Aug 1st, departing DCA at 2pm on AA 123, arriving LAX at 5pm.", and the current year is 2024, the response should be:
{"intent": "submit_travel_security_request", "entities": {"senator_name": "Senator Cruz", "travel_date": "2024-08-01", "departure": {"time": "14:00", "location": "DCA", "carrier": "AA 123"}, "arrival": {"time": "17:00", "location": "LAX"}, "details": "Travel security for trip on Aug 1st"}}
If a security admin asks "show me all committee hearing security requests", the response should be:
{"intent": "get_all_committee_hearing_security_requests", "entities": {}}
If a security admin asks "show me the last 4 hearing requests", the response should be:
{"intent": "get_all_committee_hearing_security_requests", "entities": {"limit": 4}}
If a security admin asks "list hearing security records for the BUDGET committee between June 10 and June 19", the response should be:
{"intent": "get_all_committee_hearing_security_requests", "entities": {"committee_name_filter": "BUDGET", "start_date_filter": "2024-06-10", "end_date_filter": "2024-06-19"}}
If a user says "I need hearing security for the INTELLIGENCE committee for a 'Closed hearing on Intel Matters' in SH-219 on June 22nd at 2 PM", the response should be:
{"intent": "submit_committee_hearing_security_request", "entities": {"committee_name": "INTELLIGENCE", "hearing_name": "Closed hearing on Intel Matters", "location": "SH-219", "hearing_date": "2024-06-22", "hearing_time": "14:00", "description": "Hearing security"}}
If a security admin asks "What is the most recent hearing security request?", the response should be:
{"intent": "get_most_recent_committee_hearing_security_request", "entities": {}, "format_as_table": true}
If a security admin asks "how about June 2024?", in response to seeing hearing requests for May 2024, the response should be:
{"intent": "get_all_committee_hearing_security_requests", "entities": {"start_date_filter": "2024-06-01", "end_date_filter": "2024-06-30"}}
If a security admin asks "can I see for June 2024 instead?", in response to seeing hearing requests for May 2024, the response should be:
{"intent": "get_all_committee_hearing_security_requests", "entities": {"start_date_filter": "2024-06-01", "end_date_filter": "2024-06-30"}}
If a user asks "what is my leave balance?", the response should be:
{"intent": "get_leave_balance", "entities": {}}
If the intent is unclear or cannot be mapped to the defined intents, return:
{"intent": "unknown", "entities": {}}

All extracted dates MUST be in YYYY-MM-DD format. Resolve relative dates (e.g., "tomorrow", "next week") using the current date. If a year is not specified, assume the current year. If a date is ambiguous or cannot be parsed, do not include the date key in the entities.
The "description" for "submit_it_ticket" should be the user's problem statement.
The "reason" for "request_leave" should be a concise summary.
Do not include any explanations or text outside of the JSON object.
"""

def get_intent_and_entities(message: str) -> Dict[str, Any]:
    """
    Calls Google's Gemini model to get intent and entities from a message.
    """
    logger.info(f"LLM Client: Processing message: '{message}'")
    if not model:
        logger.error("Gemini model is not initialized. Returning unknown intent.")
        return {"intent": "unknown", "entities": {}}

    current_date = datetime.now().strftime("%Y-%m-%d")
    full_prompt = f"{SYSTEM_PROMPT}\n\nToday's date is {current_date}.\n\nUser message: {message}"

    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        logger.info(f"LLM Raw Response: {response_text}")
        
        # Strip markdown JSON fence if present
        if response_text.startswith("```json"):
            response_text = response_text[7:] # Remove ```json\n
        if response_text.endswith("```"):
            response_text = response_text[:-3] # Remove ```
        response_text = response_text.strip() # Clean up any extra whitespace
        
        parsed_response = json.loads(response_text)
        intent = parsed_response.get("intent", "unknown")
        entities = parsed_response.get("entities", {})
        
        logger.info(f"LLM Client: Intent detected: {intent}, Entities: {entities}")
        return {"intent": intent, "entities": entities}

    except json.JSONDecodeError as e:
        logger.error(f"LLM Client: Failed to parse JSON response: {e}. Response was: {response_text}")
    except Exception as e: # Catch other potential errors from the API call
        logger.error(f"LLM Client: Error during API call or processing: {e}")
        
    return {"intent": "unknown", "entities": {}}