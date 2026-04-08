from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables FIRST, before importing any route or service that might need them
load_dotenv()

from app.api.routes import ai

app = FastAPI(title="Moniv8 API", description="Moniv8 Backend AI features")

# Include routers
app.include_router(ai.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Moniv8 API"}
