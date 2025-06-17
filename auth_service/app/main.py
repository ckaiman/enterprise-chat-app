from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(title="Auth Service")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Or ["*"] for all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)