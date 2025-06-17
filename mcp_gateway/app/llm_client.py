import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a real application, this module would interact with an actual LLM service.
# For demonstration, we'll use a mock implementation.

def get_intent_and_entities(message: str) -> Dict[str, Any]:
    """
    Simulates calling an LLM to get intent and entities from a message.
    """
    logger.info(f"LLM Client: Processing message: '{message}'")
    lower_message = message.lower()

    # Mocked LLM logic
    if ("how many" in lower_message or "how much" in lower_message) and ("leave" in lower_message or "vacation hours" in lower_message or "days off" in lower_message) and "available" in lower_message:
        logger.info("LLM Client: Intent detected: get_leave_balance")
        return {"intent": "get_leave_balance", "entities": {}}
    
    if "leave balance" in lower_message: # Keep simple keyword for directness
        logger.info("LLM Client: Intent detected: get_leave_balance (direct)")
        return {"intent": "get_leave_balance", "entities": {}}

    if "request leave" in lower_message or "take time off" in lower_message:
        # Basic entity extraction (very simplified)
        entities = {"leave_type": "vacation", "reason": "Not specified"}
        if "sick" in lower_message:
            entities["leave_type"] = "sick"
        # In a real LLM, you'd extract dates, specific reasons, etc.
        # For now, we'll assume the leave_client will use some defaults or a generic request.
        logger.info(f"LLM Client: Intent detected: request_leave, Entities: {entities}")
        return {"intent": "request_leave", "entities": entities}

    if "help desk" in lower_message or "it issue" in lower_message or "computer problem" in lower_message:
        entities = {"description": message} # Pass the original message as description
        if "urgent" in lower_message or "asap" in lower_message:
            entities["priority"] = "high"
        logger.info(f"LLM Client: Intent detected: submit_it_ticket, Entities: {entities}")
        return {"intent": "submit_it_ticket", "entities": entities}

    logger.info("LLM Client: Intent: unknown")
    return {"intent": "unknown", "entities": {}}