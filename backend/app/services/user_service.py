from typing import Optional
from datetime import datetime
from app.database import get_database
from app.models.user import User, UserCreate, UserUpdate, UserInDB
from app.services.auth import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.collection_name = "users"
    
    async def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        db = await get_database()
        
        # Check if user already exists
        existing_user = await db[self.collection_name].find_one({"email": user.email})
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        user_data = UserInDB(
            **user.dict(exclude={"password"}),
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await db[self.collection_name].insert_one(user_data.dict(by_alias=True))
        
        # Retrieve the created user
        created_user = await db[self.collection_name].find_one({"_id": result.inserted_id})
        return User(
            id=str(created_user["_id"]),
            email=created_user["email"],
            full_name=created_user["full_name"],
            is_active=created_user["is_active"],
            subscription_tier=created_user["subscription_tier"],
            preferences=created_user["preferences"],
            created_at=created_user["created_at"],
            updated_at=created_user["updated_at"]
        )
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        db = await get_database()
        user = await db[self.collection_name].find_one({"email": email})
        if user:
            return UserInDB(**user)
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        db = await get_database()
        try:
            from bson import ObjectId
            user = await db[self.collection_name].find_one({"_id": ObjectId(user_id)})
            if user:
                return User(
                    id=str(user["_id"]),
                    email=user["email"],
                    full_name=user["full_name"],
                    is_active=user["is_active"],
                    subscription_tier=user["subscription_tier"],
                    preferences=user["preferences"],
                    created_at=user["created_at"],
                    updated_at=user["updated_at"]
                )
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
        return None
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with email and password"""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db = await get_database()
        
        try:
            from bson import ObjectId
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
                    full_name=updated_user["full_name"],
                    is_active=updated_user["is_active"],
                    subscription_tier=updated_user["subscription_tier"],
                    preferences=updated_user["preferences"],
                    created_at=updated_user["created_at"],
                    updated_at=updated_user["updated_at"]
                )
            
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None

# Global user service instance
user_service = UserService()