from fastapi import APIRouter, Depends, HTTPException
from .models import SecurityIncidentReport, SecurityIncidentResponse, TravelSecurityRequestData, TravelSecurityRequestResponse
from .auth_middleware import verify_token_dependency
from .security_client import example_call_external_api # Example client
from .mock_db import mock_incidents_db, mock_travel_security_requests_db # Import new mock_db
import logging # Import the logging module
import uuid

router = APIRouter()

# Get a logger instance
logger = logging.getLogger(__name__)

# In-memory store for this example

@router.post("/incidents", response_model=SecurityIncidentResponse)
async def report_security_incident(
    incident_data: SecurityIncidentReport, 
    user_auth_data: dict = Depends(verify_token_dependency)
):
    user_email = user_auth_data.get("sub")
    incident_id = str(uuid.uuid4())
    
    new_incident = SecurityIncidentResponse(
        incident_id=incident_id,
        status="reported",
        reported_by_email=user_email,
        **incident_data.model_dump()
    )
    mock_incidents_db.append(new_incident.model_dump())
    # Optionally, call the external API via security_client
    # example_call_external_api("some_endpoint", new_incident.model_dump())
    return new_incident

@router.post("/travel-requests", response_model=TravelSecurityRequestResponse)
async def submit_travel_security_request(
    request_data: TravelSecurityRequestData,
    user_auth_data: dict = Depends(verify_token_dependency)
):
    user_email = user_auth_data.get("sub")
    request_id = str(uuid.uuid4())

    new_travel_request = TravelSecurityRequestResponse(
        request_id=request_id,
        status="received",
        reported_by_email=user_email, # This is now the only source for this field
        **request_data.model_dump()
    )
    mock_travel_security_requests_db.append(new_travel_request.model_dump())
    # Optionally, call the external API via security_client for travel requests
    # example_call_external_api("travel_security_endpoint", new_travel_request.model_dump())
    
    logger.info(f"Received travel security request: {new_travel_request.model_dump()}")
    return new_travel_request