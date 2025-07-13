from bson import ObjectId
from app.models.document import Document, DocumentInDB
from app.database import get_database
from app.services.ai_service import ai_service

class DocumentService:
    def __init__(self, db_collection):
        self.collection = db_collection

    async def create_document(self, document: Document, user_id: str):
        stats = ai_service.calculate_writing_stats(document.content)
        doc_data = document.dict()
        doc_data["user_id"] = user_id
        doc_data.update(stats)
        created = await self.collection.insert_one(doc_data)
        created_doc = await self.collection.find_one({"_id": created.inserted_id})
        if "_id" in created_doc:
            created_doc["_id"] = str(created_doc["_id"])
        return Document.from_db(DocumentInDB(**created_doc))

    async def get_documents_by_user(self, user_id: str):
        cursor = self.collection.find({"user_id": user_id})
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(Document.from_db(DocumentInDB(**doc)))
        return documents

    async def get_document(self, doc_id: str, user_id: str = None):
        try:
            obj_id = ObjectId(doc_id)
        except Exception:
            return None

        query = {"_id": obj_id}
        if user_id:
            query["user_id"] = user_id

        doc = await self.collection.find_one(query)
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return Document.from_db(DocumentInDB(**doc))


# Shared service instance — will be initialized in main.py
document_service: DocumentService = None

def get_document_service():
    if document_service is None:
        raise RuntimeError("❌ document_service is not initialized!")
    return document_service
