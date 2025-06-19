from pydantic import BaseModel
from typing import Optional

class SecurityIncidentReport(BaseModel):
    incident_type: str
    location: str
    description: str
    reported_by_email: Optional[str] = None # Will be filled from token

class SecurityIncidentResponse(SecurityIncidentReport):
    incident_id: str
    status: str

class TravelSecurityRequestData(BaseModel):
    senator_name: Optional[str] = None
    request_type: Optional[str] = None # e.g., "Briefing", "Assessment", "Support"
    travel_type: Optional[str] = None # e.g., "Official", "Campaign", "Personal"
    travel_type_other: Optional[str] = None
    travel_date: Optional[str] = None # Expected YYYY-MM-DD
    details: Optional[str] = None # General description or incident details

class TravelSecurityRequestResponse(TravelSecurityRequestData):
    request_id: str
    status: str