from pydantic import BaseModel
from typing import Optional

class TravelLeg(BaseModel):
    time: Optional[str] = None # e.g., "14:30"
    location: Optional[str] = None # e.g., "DCA", "Union Station", "123 Main St"
    carrier: Optional[str] = None # e.g., "American Airlines AA123", "Amtrak 50", "Official Vehicle"

class TravelSecurityRequestData(BaseModel):
    senator_name: Optional[str] = None
    request_type: Optional[str] = None # e.g., "Briefing", "Assessment", "Support"
    travel_type: Optional[str] = None # e.g., "Official", "Campaign", "Personal"
    travel_type_other: Optional[str] = None
    travel_date: Optional[str] = None # Expected YYYY-MM-DD. Represents the primary date of travel.
    details: Optional[str] = None # General description or incident details
    departure: Optional[TravelLeg] = None
    arrival: Optional[TravelLeg] = None

class TravelSecurityRequestResponse(TravelSecurityRequestData):
    request_id: str
    status: str
    reported_by_email: Optional[str] = None