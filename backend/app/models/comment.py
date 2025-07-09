from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId
from app.models.suggestion import SuggestionPosition

class CommentBase(BaseModel):
    document_id: str
    text: str
    position: SuggestionPosition

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    text: Optional[str] = None
    resolved: Optional[bool] = None

class CommentInDB(CommentBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    author: str  # User's full name
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Comment(CommentBase):
    id: str
    user_id: str
    author: str
    resolved: bool
    created_at: datetime
    updated_at: datetime
    timestamp: datetime  # Alias for created_at for frontend compatibility

    @classmethod
    def from_db(cls, comment_in_db: CommentInDB):
        comment_dict = comment_in_db.dict()
        comment_dict["id"] = str(comment_dict["id"])
        comment_dict["timestamp"] = comment_dict["created_at"]
        return cls(**comment_dict)