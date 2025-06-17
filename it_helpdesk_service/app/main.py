from fastapi import FastAPI, status
from .routes import router
from .models import TicketRequest, TicketStatus
from .mock_db import mock_tickets, mock_categories

app = FastAPI(title="IT Help Desk API")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)