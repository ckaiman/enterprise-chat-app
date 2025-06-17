from fastapi import FastAPI
from .routes import router
from .models import TicketRequest, TicketStatus
from .mock_db import mock_tickets, mock_categories

app = FastAPI(title="IT Help Desk API")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)