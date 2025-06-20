from fastapi import APIRouter, Depends, HTTPException
from .models import CommitteeHearingSecurityRequest, CommitteeHearingSecurityResponse, CommitteeHearingData
from .auth_middleware import verify_token_dependency, verify_security_admin_role
from .mock_db import mock_hearing_security_requests, next_mock_id # Import mock db and counter
from datetime import datetime, timezone
import uuid
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/security", response_model=CommitteeHearingSecurityResponse)
async def create_hearing_security_request(
    request_data: CommitteeHearingSecurityRequest,
    user_auth_data: dict = Depends(verify_token_dependency)
):
    global next_mock_id
    user_email = user_auth_data.get("sub")
    
    # Create a new response object with generated fields
    new_request = CommitteeHearingSecurityResponse(
        id=next_mock_id,
        created_by=user_email,
        committee_hearing_uuid=uuid.uuid4(),
        datetime_created=datetime.now(timezone.utc),
        datetime_updated=datetime.now(timezone.utc),
        **request_data.model_dump() # Spread the incoming data
    )
    
    # Store in mock DB (in a real app, this would be a database insert)
    mock_hearing_security_requests.append(new_request.model_dump())
    next_mock_id += 1
    
    logger.info(f"Created hearing security request: {new_request.model_dump()}")
    return new_request

@router.get("/security/all", response_model=list[CommitteeHearingSecurityResponse])
async def get_all_hearing_security_requests(
    user_auth_data: dict = Depends(verify_security_admin_role) # Requires security_admin role
):
    """Return all committee hearing security requests (security_admin only)"""
    logger.info(f"Security admin {user_auth_data.get('sub')} requested all hearing security requests.")
    # In a real app, you'd fetch this from the database
    return mock_hearing_security_requests