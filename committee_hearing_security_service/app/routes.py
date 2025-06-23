from fastapi import APIRouter, Depends, HTTPException, Query
from .models import CommitteeHearingSecurityRequest, CommitteeHearingSecurityResponse, CommitteeHearingData
from .auth_middleware import verify_token_dependency, verify_security_admin_role
from .mock_db import mock_hearing_security_requests, next_mock_id # Import mock db and counter
from datetime import datetime, timezone
from typing import Optional, List # Import List and Optional
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

@router.get("/security/all", response_model=List[CommitteeHearingSecurityResponse])
async def get_all_hearing_security_requests(
    user_auth_data: dict = Depends(verify_security_admin_role),
    committee_name: Optional[str] = Query(None, alias="committeeNameFilter"),
    location: Optional[str] = Query(None, alias="locationFilter"),
    level: Optional[str] = Query(None, alias="levelFilter"),
    start_date_filter: Optional[str] = Query(None, alias="startDateFilter", description="YYYY-MM-DD"),
    end_date_filter: Optional[str] = Query(None, alias="endDateFilter", description="YYYY-MM-DD"),
    limit: Optional[int] = Query(None, description="Limit the number of results returned")
):
    """Return all committee hearing security requests (security_admin only)"""
    logger.info(f"Security admin {user_auth_data.get('sub')} requested hearing security requests with filters: committee_name={committee_name}, location={location}, level={level}, start_date={start_date_filter}, end_date={end_date_filter}.")
    
    filtered_requests = list(mock_hearing_security_requests) # Start with a copy

    if committee_name:
        filtered_requests = [
            req for req in filtered_requests
            if req["committee_hearing_data"].get("committee_name", "").lower() == committee_name.lower()
        ]
    
    if location:
        filtered_requests = [
            req for req in filtered_requests
            if req["committee_hearing_data"].get("location", "").lower() == location.lower()
        ]

    if level:
        filtered_requests = [
            req for req in filtered_requests
            if req.get("level", "").lower() == level.lower()
        ]

    if start_date_filter:
        try:
            s_date_naive = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            filtered_requests = [req for req in filtered_requests if req.get("datetime_incident") and req["datetime_incident"].date() >= s_date_naive]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date_filter format. Use YYYY-MM-DD.")

    if end_date_filter:
        try:
            e_date_naive = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            filtered_requests = [req for req in filtered_requests if req.get("datetime_incident") and req["datetime_incident"].date() <= e_date_naive]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date_filter format. Use YYYY-MM-DD.")

    # Sort by incident date descending to get the most recent ones first.
    # This handles the "last X" type of requests.
    # We provide a default for None dates to prevent sorting errors.
    filtered_requests.sort(
        key=lambda x: x.get("datetime_incident") or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )

    if limit:
        filtered_requests = filtered_requests[:limit]

    return filtered_requests

@router.get("/security/most-recent", response_model=Optional[CommitteeHearingSecurityResponse])
async def get_most_recent_hearing_security_request(
    user_auth_data: dict = Depends(verify_security_admin_role) # Requires security_admin role
):
    """Return the most recent committee hearing security request (security_admin only)"""
    logger.info(f"Security admin {user_auth_data.get('sub')} requested the most recent hearing security request.")
    if not mock_hearing_security_requests:
        return None # Or raise HTTPException(status_code=404, detail="No hearing security requests found")
    
    # Sort by datetime_created in descending order and get the first one
    most_recent_request = sorted(mock_hearing_security_requests, key=lambda x: x['datetime_created'], reverse=True)[0]
    return most_recent_request