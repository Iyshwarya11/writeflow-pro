from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, documents, suggestions, analytics, comments
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up WriteFlow Pro API...")
    await connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down WriteFlow Pro API...")
    await close_mongo_connection()

app = FastAPI(
    title="WriteFlow Pro API",
    description="AI-powered writing assistant API with grammar checking, style suggestions, and real-time collaboration",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(suggestions.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(comments.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to WriteFlow Pro API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WriteFlow Pro API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)