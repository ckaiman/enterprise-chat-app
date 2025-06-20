from datetime import datetime, timezone, timedelta # Import timedelta
import uuid

# Helper to create timezone-aware datetime
def tz_datetime(year, month, day, hour, minute, second=0, microsecond=0, tz_offset_hours=-4):
    return datetime(year, month, day, hour, minute, second, microsecond, tzinfo=timezone(timedelta(hours=tz_offset_hours)))

# Mock database for committee hearing security requests
mock_hearing_security_requests = [
    {
        "id": 2320,
        "created_by": "bob@example.com",
        "committee_hearing_data": {
            "name": "Closed hearing on Intelligence Matters",
            "location": "SH-219",
            "committee_name": "INTELLIGENCE"
        },
        "committee_hearing_uuid": uuid.uuid4(),
        "description": "Staff and Members gathered throughout hearing rooms. Media is present but orderly. USCP is monitoring/posted as requested. Checked in with staff - Appreciative of support. No issues or disruptions expected.",
        "datetime_incident": tz_datetime(2025, 6, 18, 14, 5),
        "datetime_created": tz_datetime(2025, 6, 18, 14, 5, 38, 147375),
        "datetime_updated": tz_datetime(2025, 6, 18, 14, 5, 38, 147392),
        "is_normal": True,
        "level": "Green",
        "photo": ""
    },
    {
        "id": 2321,
        "created_by": "alice@example.com",
        "committee_hearing_data": {
            "name": "Open hearing on Budget Priorities",
            "location": "SD-608",
            "committee_name": "BUDGET"
        },
        "committee_hearing_uuid": uuid.uuid4(),
        "description": "Standard security presence. No issues.",
        "datetime_incident": tz_datetime(2025, 6, 19, 10, 0),
        "datetime_created": tz_datetime(2025, 6, 19, 10, 1, 10, 500000),
        "datetime_updated": tz_datetime(2025, 6, 19, 10, 1, 10, 500000),
        "is_normal": True,
        "level": "Green",
        "photo": ""
    },
    # Add 8 more similar mock entries here...
    # Ensure unique IDs and UUIDs for each entry
]

# Simple counter for mock IDs
next_mock_id = max([req['id'] for req in mock_hearing_security_requests]) + 1 if mock_hearing_security_requests else 1