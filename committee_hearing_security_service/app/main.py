from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(title="Committee Hearing Security Service")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

app.include_router(router, prefix="/hearings", tags=["hearings"]) # Added prefix

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security, e.g., your MCP Gateway's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)