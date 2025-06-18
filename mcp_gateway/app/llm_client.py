import logging
from typing import Dict, Any
import os
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
The possible intents are: "get_leave_balance", "request_leave", "submit_it_ticket", "get_account_info", "unknown".

For "request_leave", extract: "leave_type" (e.g., "vacation", "sick"), "start_date" (YYYY-MM-DD), "end_date" (YYYY-MM-DD), "reason" (a summary of the leave request).
For "submit_it_ticket", extract: "category" (e.g., "hardware", "software", "network", "email", "account", "other"), "priority" (e.g., "low", "medium", "high"), "description" (the user's full issue statement). If the user describes a problem like "I'm having trouble with X" or "X is not working", this is likely a "submit_it_ticket" intent. The "description" should be the user's problem. If a category isn't explicit, try to infer one (e.g., "email issue" -> category: "email") or use "other".
For "get_account_info", if the user asks about their email, name, or role, this is the intent. No specific entities are needed beyond the intent.
For "get_leave_balance", no specific entities are needed beyond the intent.

You MUST respond with ONLY a valid JSON object. The JSON object must have two keys: "intent" (string) and "entities" (object).
Example for "request_leave":
{"intent": "request_leave", "entities": {"leave_type": "sick", "start_date": "2024-01-10", "reason": "Feeling unwell"}}
Example for "submit_it_ticket":
{"intent": "submit_it_ticket", "entities": {"category": "software", "priority": "medium", "description": "My email client is crashing."}}
If the user says "I'm having email trouble", the response should be:
{"intent": "submit_it_ticket", "entities": {"category": "email", "description": "I'm having email trouble"}}
If the user asks "what is my email address?" or "who am i?", the response should be:
{"intent": "get_account_info", "entities": {}}
Example for "get_leave_balance":
{"intent": "get_leave_balance", "entities": {}}
If the intent is unclear or cannot be mapped to the defined intents, return:
{"intent": "unknown", "entities": {}}

Ensure dates are in YYYY-MM-DD format. If a date cannot be parsed, return the original string for that date field.
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

    full_prompt = f"{SYSTEM_PROMPT}\n\nUser message: {message}"

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