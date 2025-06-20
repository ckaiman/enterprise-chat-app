from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CommitteeHearingData(BaseModel):
    name: str
    location: str
    committee_name: str

class CommitteeHearingSecurityRequest(BaseModel):
    committee_hearing_data: CommitteeHearingData
    description: Optional[str] = None
    datetime_incident: Optional[datetime] = None # Use datetime type
    is_normal: bool = True
    level: Optional[str] = None
    photo: Optional[str] = None # Assuming base64 or URL

class CommitteeHearingSecurityResponse(CommitteeHearingSecurityRequest):
    id: int # Mock ID
    created_by: Optional[str] = None # Email from token
    committee_hearing_uuid: uuid.UUID # Use UUID type
    datetime_created: datetime
    datetime_updated: datetime