from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings
from routers.generate import router as generate_router
from middleware.quota import QuotaMiddleware

# Initialize FastAPI app
app = FastAPI(
    title="RizzGPT Clone API",
    description="Backend API for RizzGPT Clone - AI-powered dating conversation assistant",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add quota middleware
app.add_middleware(QuotaMiddleware, free_tier_limit=5)

# Include routers
app.include_router(generate_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "RizzGPT Clone API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )