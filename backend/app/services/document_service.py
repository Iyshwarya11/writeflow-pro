from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_database
from app.models.document import Document, DocumentCreate, DocumentUpdate, DocumentInDB
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.collection_name = "documents"
    
    async def create_document(self, document: DocumentCreate, user_id: str) -> Document:
        """Create a new document"""
        db = await get_database()
        
        # Calculate initial stats
        stats = ai_service.calculate_writing_stats(document.content)
        
        document_data = DocumentInDB(
            **document.dict(),
            user_id=user_id,
            word_count=stats.word_count,
            reading_time=stats.reading_time,
            version=1,
            collaborators=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await db[self.collection_name].insert_one(document_data.dict(by_alias=True))
        
        # Retrieve the created document
        created_doc = await db[self.collection_name].find_one({"_id": result.inserted_id})
        return Document.from_db(DocumentInDB(**created_doc))
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get a document by ID"""
        db = await get_database()
        
        try:
            doc = await db[self.collection_name].find_one({
                "_id": ObjectId(document_id),
                "user_id": user_id
            })
            
            if doc:
                return Document.from_db(DocumentInDB(**doc))
            return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None
    
    async def get_user_documents(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get all documents for a user"""
        db = await get_database()
        
        cursor = db[self.collection_name].find(
            {"user_id": user_id}
        ).sort("updated_at", -1).skip(skip).limit(limit)
        
        documents = []
        async for doc in cursor:
            documents.append(Document.from_db(DocumentInDB(**doc)))
        
        return documents
    
    async def update_document(self, document_id: str, document_update: DocumentUpdate, user_id: str) -> Optional[Document]:
        """Update a document"""
        db = await get_database()
        
        try:
            update_data = {k: v for k, v in document_update.dict().items() if v is not None}
            
            if "content" in update_data:
                # Recalculate stats if content changed
                stats = ai_service.calculate_writing_stats(update_data["content"])
                update_data.update({
                    "word_count": stats.word_count,
                    "reading_time": stats.reading_time,
                    "version": {"$inc": 1}  # Increment version
                })
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Handle version increment separately
            version_inc = update_data.pop("version", None)
            update_query = {"$set": update_data}
            if version_inc:
                update_query["$inc"] = {"version": 1}
            
            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(document_id), "user_id": user_id},
                update_query
            )
            
            if result.modified_count:
                updated_doc = await db[self.collection_name].find_one({
                    "_id": ObjectId(document_id),
                    "user_id": user_id
                })
                return Document.from_db(DocumentInDB(**updated_doc))
            
            return None
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return None
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document"""
        db = await get_database()
        
        try:
            result = await db[self.collection_name].delete_one({
                "_id": ObjectId(document_id),
                "user_id": user_id
            })
            
            # Also delete related suggestions and comments
            await db["suggestions"].delete_many({"document_id": document_id})
            await db["comments"].delete_many({"document_id": document_id})
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def duplicate_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """Duplicate a document"""
        original_doc = await self.get_document(document_id, user_id)
        if not original_doc:
            return None
        
        # Create new document with modified title
        new_doc_data = DocumentCreate(
            title=f"{original_doc.title} (Copy)",
            content=original_doc.content,
            tags=original_doc.tags,
            language=original_doc.language,
            writing_goal=original_doc.writing_goal,
            is_public=False,  # Copies are private by default
            shared=False,
            starred=False
        )
        
        return await self.create_document(new_doc_data, user_id)
    
    async def search_documents(self, user_id: str, query: str, skip: int = 0, limit: int = 50) -> List[Document]:
        """Search documents by title and content"""
        db = await get_database()
        
        search_query = {
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}}
            ]
        }
        
        cursor = db[self.collection_name].find(search_query).sort("updated_at", -1).skip(skip).limit(limit)
        
        documents = []
        async for doc in cursor:
            documents.append(Document.from_db(DocumentInDB(**doc)))
        
        return documents

# Global document service instance
document_service = DocumentService()