from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import auth, documents, suggestions, analytics, comments
import app.services.document_service as ds_module  # Used for assigning shared instance
from app.services.document_service import DocumentService
from app.config import settings

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     logger.info("Starting up WriteFlow Pro API...")
#     await connect_to_mongo()
#     yield
#     # Shutdown
#     logger.info("Shutting down WriteFlow Pro API...")
#     await close_mongo_connection()

app = FastAPI(
    title="WriteFlow Pro API",
    version="1.0.0",
    description="Backend for the AI-powered writing assistant 📝"
)

# CORS settings — allow all origins for dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- App Startup Event ---
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    db = await get_database()
    
    # ✅ Shared DocumentService initialized for app-wide use
    ds_module.document_service = DocumentService(db["documents"])
    print("✅ document_service initialized")

# --- App Shutdown Event ---
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# --- Register routers ---
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(documents.router, prefix="/api/auth/documents", tags=["documents"])
app.include_router(suggestions.router, prefix="/api/ai", tags=["ai-suggestions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])

# --- Root Route ---
@app.get("/")
async def root():
    return {"message": "WriteFlow Pro API is running 📝"}

# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}
