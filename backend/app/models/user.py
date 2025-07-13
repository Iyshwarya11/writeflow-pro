from bson import ObjectId
from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr, Field
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue


# -------------------------------
# ✅ MongoDB ObjectId Support (Pydantic v2)
# -------------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v: Any) -> "PyObjectId":
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: GetCoreSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string"}


# -------------------------------
# ✅ Base Schema for All Users
# -------------------------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True
    subscription_tier: str = "free"
    preferences: Dict[str, Any] = {}


# -------------------------------
# ✅ User Creation (Signup)
# -------------------------------
class UserCreate(UserBase):
    password: str


# -------------------------------
# ✅ User Update (Patch Profile)
# -------------------------------
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    subscription_tier: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


# -------------------------------
# ✅ MongoDB Document Model
# -------------------------------
class UserInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    hashed_password: str
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    subscription_tier: Optional[str] = "free"
    preferences: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# -------------------------------
# ✅ Sent to Frontend (Clean Version)
# -------------------------------
class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


# -------------------------------
# ✅ Auth Token Schemas
# -------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
