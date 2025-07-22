# MongoDB Database Configuration
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo import ReturnDocument
from datetime import datetime
import os
from typing import Optional, List, Dict
from bson import ObjectId

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = "grammarly_clone"
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client[self.database_name]
        
        # Create indexes
        await self.create_indexes()
    
    async def create_indexes(self):
        """Create database indexes for better performance"""
        # Documents collection indexes
        await self.db.documents.create_index("user_id")
        await self.db.documents.create_index("created_at")
        await self.db.documents.create_index("last_modified")
        
        # Suggestions collection indexes
        await self.db.suggestions.create_index("document_id")
        await self.db.suggestions.create_index("created_at")
        
        # Plagiarism results indexes
        await self.db.plagiarism_results.create_index("document_id")
        await self.db.plagiarism_results.create_index("created_at")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    # Document operations
    async def save_document(self, user_id: str, title: str, content: str, score: int = 0, document_id: Optional[str] = None):
        """Save or update a document"""
        document = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "word_count": len(content.split()),
            "character_count": len(content),
            "score": score,
            "last_modified": datetime.utcnow()
        }
        
        if document_id:
            # Update existing document
            await self.db.documents.update_one(
                {"_id": document_id},
                {"$set": document}
            )
            return document_id
        else:
            # Create new document
            document["created_at"] = datetime.utcnow()
            result = await self.db.documents.insert_one(document)
            return str(result.inserted_id)
    
    async def get_document(self, document_id: str):
        """Get a document by ID"""
        return await self.db.documents.find_one({"_id": document_id})
    
    async def get_user_documents(self, user_id: str, limit: int = 10):
        """Get user's documents"""
        cursor = self.db.documents.find({"user_id": user_id}).sort("last_modified", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def delete_document(self, document_id: str):
        """Delete a document"""
        await self.db.documents.delete_one({"_id": ObjectId(document_id)})
    
    # Suggestions operations
    async def save_suggestions(self, document_id: str, suggestions: List[Dict]):
        """Save suggestions for a document"""
        suggestion_doc = {
            "document_id": document_id,
            "suggestions": suggestions,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.suggestions.insert_one(suggestion_doc)
        return str(result.inserted_id)
    
    async def get_suggestions(self, document_id: str):
        """Get suggestions for a document"""
        return await self.db.suggestions.find_one(
            {"document_id": document_id},
            sort=[("created_at", -1)]
        )
    
    # Plagiarism results operations
    async def save_plagiarism_result(self, document_id: str, overall_score: float, results: List[Dict]):
        """Save plagiarism check results"""
        result_doc = {
            "document_id": document_id,
            "overall_score": overall_score,
            "results": results,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.plagiarism_results.insert_one(result_doc)
        return str(result.inserted_id)
    
    async def get_plagiarism_result(self, document_id: str):
        """Get plagiarism results for a document"""
        return await self.db.plagiarism_results.find_one(
            {"document_id": document_id},
            sort=[("created_at", -1)]
        )
    
    # Analytics operations
    async def get_user_statistics(self, user_id: str, days: int = 7):
        """Get user writing statistics"""
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get documents created in the time period
        documents = await self.db.documents.find({
            "user_id": user_id,
            "created_at": {"$gte": start_date}
        }).to_list(length=None)
        
        # Calculate statistics
        total_words = sum(doc.get("word_count", 0) for doc in documents)
        total_documents = len(documents)
        
        # Get suggestions statistics
        suggestion_cursor = self.db.suggestions.find({
            "document_id": {"$in": [doc["_id"] for doc in documents]}
        })
        
        suggestions = await suggestion_cursor.to_list(length=None)
        
        # Count suggestion types
        suggestion_counts = {}
        for suggestion_doc in suggestions:
            for suggestion in suggestion_doc.get("suggestions", []):
                suggestion_type = suggestion.get("type", "other")
                suggestion_counts[suggestion_type] = suggestion_counts.get(suggestion_type, 0) + 1
        
        return {
            "total_words": total_words,
            "total_documents": total_documents,
            "suggestion_counts": suggestion_counts,
            "period_days": days
        }
    
    async def get_writing_trends(self, user_id: str, days: int = 30):
        """Get writing trends over time"""
        from datetime import datetime, timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "words": {"$sum": "$word_count"},
                    "documents": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id": 1}
            }
        ]
        
        cursor = self.db.documents.aggregate(pipeline)
        return await cursor.to_list(length=None)

    # User management
    async def upsert_user(self, email: str, extra_fields: dict = None):
        now = datetime.utcnow()
        user_doc = {
            "email": email,
            "last_login": now,
        }
        if extra_fields:
            user_doc.update(extra_fields)
        return await self.db.users.find_one_and_update(
            {"email": email},
            {"$setOnInsert": {"created_at": now}, "$set": user_doc},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

    async def get_user(self, email: str):
        return await self.db.users.find_one({"email": email})

# Global database manager instance
db_manager = DatabaseManager()