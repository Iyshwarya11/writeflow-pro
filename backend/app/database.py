# app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, TEXT
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

# ✅ Proper get_database method
async def get_database():
    if db.database is None:
        raise RuntimeError("❌ MongoDB not initialized. Did you forget to call connect_to_mongo?")
    return db.database

# ✅ Connect to MongoDB
async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]

        # Test connection
        await db.client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully")

        # Create indexes
        await create_indexes()

    except Exception as e:
        # logger.error(f"❌ Failed to connect to MongoDB: {e}")
        # raise
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Don't raise in development - allow app to start without MongoDB
        logger.warning("Starting without MongoDB connection - some features may not work")

# ✅ Close MongoDB connection
async def close_mongo_connection():
    if db.client:
        db.client.close()
        logger.info("🔌 Disconnected from MongoDB")

# ✅ Index creation
async def create_indexes():
    try:
        # Users
        await db.database.users.create_index([("email", ASCENDING)], unique=True)

        # Documents
        await db.database.documents.create_index([("user_id", ASCENDING)])
        await db.database.documents.create_index([("title", TEXT), ("content", TEXT)])
        await db.database.documents.create_index([("created_at", ASCENDING)])
        await db.database.documents.create_index([("updated_at", ASCENDING)])

        # Suggestions
        await db.database.suggestions.create_index([("document_id", ASCENDING)])
        await db.database.suggestions.create_index([("user_id", ASCENDING)])
        await db.database.suggestions.create_index([("created_at", ASCENDING)])

        # Comments
        await db.database.comments.create_index([("document_id", ASCENDING)])
        await db.database.comments.create_index([("user_id", ASCENDING)])

        logger.info("✅ Indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
