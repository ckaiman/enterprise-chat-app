from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import ALLOWED_ORIGINS

app = FastAPI(title="Auth Service")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy"}

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)