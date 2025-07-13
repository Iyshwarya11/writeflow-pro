from typing import Optional
from datetime import datetime
import logging

from bson import ObjectId
from app.database import get_database
from app.models.user import User, UserCreate, UserUpdate, UserInDB
from app.services.auth import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.collection_name = "users"

    async def create_user(self, user: UserCreate) -> User:
        db = await get_database()
        existing_user = await db[self.collection_name].find_one({"email": user.email})
        if existing_user:
            raise ValueError("User with this email already exists")

        now = datetime.utcnow()
        hashed_password = get_password_hash(user.password)
        user_data = {
            "email": user.email,
            "full_name": user.full_name,
            "hashed_password": hashed_password,
            "is_active": user.is_active,
            "subscription_tier": user.subscription_tier,
            "preferences": user.preferences,
            "created_at": now,
            "updated_at": now
        }

        result = await db[self.collection_name].insert_one(user_data)
        created_user = await db[self.collection_name].find_one({"_id": result.inserted_id})
        return User(
            id=str(created_user["_id"]),
            email=created_user["email"],
            full_name=created_user.get("full_name", ""),
            is_active=created_user.get("is_active", True),
            subscription_tier=created_user.get("subscription_tier", "free"),
            preferences=created_user.get("preferences", {}),
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"]
        )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        db = await get_database()
        user = await db[self.collection_name].find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])  # Convert ObjectId to string
            return UserInDB(**user)
        return None

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        db = await get_database()
        try:
            user = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
            if user:
                return User(
                    id=str(user["_id"]),
                    email=user["email"],
                    full_name=user.get("full_name", ""),
                    is_active=user.get("is_active", True),
                    subscription_tier=user.get("subscription_tier", "free"),
                    preferences=user.get("preferences", {}),
                    created_at=user["created_at"],
                    updated_at=user["updated_at"]
                )
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
        return None

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        user = await self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        db = await get_database()
        try:
            update_data = {k: v for k, v in user_update.dict().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()

            result = await db[self.collection_name].update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

            if result.modified_count:
                updated_user = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
                return User(
                    id=str(updated_user["_id"]),
                    email=updated_user["email"],
                    full_name=updated_user.get("full_name", ""),
                    is_active=updated_user.get("is_active", True),
                    subscription_tier=updated_user.get("subscription_tier", "free"),
                    preferences=updated_user.get("preferences", {}),
                    created_at=updated_user["created_at"],
                    updated_at=updated_user["updated_at"]
                )
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

# Global user service instance
user_service = UserService()
