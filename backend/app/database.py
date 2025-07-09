from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, TEXT
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Users collection indexes
        users_collection = db.database.users
        await users_collection.create_index([("email", ASCENDING)], unique=True)
        
        # Documents collection indexes
        documents_collection = db.database.documents
        await documents_collection.create_index([("user_id", ASCENDING)])
        await documents_collection.create_index([("title", TEXT), ("content", TEXT)])
        await documents_collection.create_index([("created_at", ASCENDING)])
        await documents_collection.create_index([("updated_at", ASCENDING)])
        
        # Suggestions collection indexes
        suggestions_collection = db.database.suggestions
        await suggestions_collection.create_index([("document_id", ASCENDING)])
        await suggestions_collection.create_index([("user_id", ASCENDING)])
        await suggestions_collection.create_index([("created_at", ASCENDING)])
        
        # Comments collection indexes
        comments_collection = db.database.comments
        await comments_collection.create_index([("document_id", ASCENDING)])
        await comments_collection.create_index([("user_id", ASCENDING)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")