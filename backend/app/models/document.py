from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class DocumentBase(BaseModel):
    title: str
    content: str = ""
    tags: List[str] = []
    language: str = "en-US"
    writing_goal: str = "professional"
    is_public: bool = False
    shared: bool = False
    starred: bool = False

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    language: Optional[str] = None
    writing_goal: Optional[str] = None
    is_public: Optional[bool] = None
    shared: Optional[bool] = None
    starred: Optional[bool] = None

class DocumentInDB(DocumentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    word_count: int = 0
    reading_time: int = 0
    version: int = 1
    collaborators: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Document(DocumentBase):
    id: str
    user_id: str
    word_count: int
    reading_time: int
    version: int
    collaborators: List[str]
    created_at: datetime
    updated_at: datetime
    last_modified: datetime  # Alias for updated_at for frontend compatibility

    @classmethod
    def from_db(cls, doc_in_db: DocumentInDB):
        doc_dict = doc_in_db.dict()
        doc_dict["id"] = str(doc_dict["id"])
        doc_dict["last_modified"] = doc_dict["updated_at"]
        return cls(**doc_dict)