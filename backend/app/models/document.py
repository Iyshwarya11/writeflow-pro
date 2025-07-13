from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId


# ----------------------------
# ✅ Base Schema
# ----------------------------

class DocumentBase(BaseModel):
    title: str
    content: str = ""
    tags: List[str] = []
    language: str = "en-US"
    writing_goal: str = "professional"
    is_public: bool = False
    shared: bool = False
    starred: bool = False


# ----------------------------
# ✅ Document Create/Update DTOs
# ----------------------------

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


# ----------------------------
# ✅ MongoDB Model (Internal DB Use)
# ----------------------------

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
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        populate_by_name = True


# ----------------------------
# ✅ Final API Model (Frontend/Client Use)
# ----------------------------

class Document(DocumentBase):
    id: str
    user_id: str
    word_count: int
    reading_time: int
    version: int
    collaborators: List[str]
    created_at: datetime
    updated_at: datetime
    last_modified: datetime  # alias for updated_at (frontend-friendly)

    @classmethod
    def from_db(cls, doc_in_db: DocumentInDB):
        doc_dict = doc_in_db.dict(by_alias=True)

        # Remove internal _id to prevent validation error
        if "_id" in doc_dict:
            doc_dict["id"] = str(doc_dict.pop("_id"))

        doc_dict["last_modified"] = doc_dict["updated_at"]

        return cls(**doc_dict)
