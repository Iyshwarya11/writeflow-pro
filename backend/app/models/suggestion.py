from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.models.user import PyObjectId

class SuggestionPosition(BaseModel):
    start: int
    end: int

class SuggestionBase(BaseModel):
    document_id: str
    type: str  # grammar, style, clarity, tone, plagiarism, vocabulary
    text: str
    suggestion: str
    explanation: str
    position: SuggestionPosition
    severity: str = "info"  # error, warning, info
    confidence: float = 0.0

class SuggestionCreate(SuggestionBase):
    pass

class SuggestionUpdate(BaseModel):
    is_applied: Optional[bool] = None
    is_dismissed: Optional[bool] = None

class SuggestionInDB(SuggestionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    is_applied: bool = False
    is_dismissed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Suggestion(SuggestionBase):
    id: str
    user_id: str
    is_applied: bool
    is_dismissed: bool
    created_at: datetime

    @classmethod
    def from_db(cls, suggestion_in_db: SuggestionInDB):
        suggestion_dict = suggestion_in_db.dict()
        suggestion_dict["id"] = str(suggestion_dict["id"])
        return cls(**suggestion_dict)