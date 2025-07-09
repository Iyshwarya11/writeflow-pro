from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.comment import Comment, CommentCreate, CommentUpdate, CommentInDB
from app.models.user import User
from app.services.document_service import document_service
from app.database import get_database
from app.dependencies import get_current_active_user
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=Comment)
async def create_comment(
    comment: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new comment"""
    # Verify document ownership or access
    document = await document_service.get_document(comment.document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db = await get_database()
    
    comment_data = CommentInDB(
        **comment.dict(),
        user_id=current_user.id,
        author=current_user.full_name,
        resolved=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    result = await db["comments"].insert_one(comment_data.dict(by_alias=True))
    
    # Retrieve the created comment
    created_comment = await db["comments"].find_one({"_id": result.inserted_id})
    return Comment.from_db(CommentInDB(**created_comment))

@router.get("/document/{document_id}", response_model=List[Comment])
async def get_document_comments(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all comments for a document"""
    # Verify document ownership or access
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db = await get_database()
    cursor = db["comments"].find({"document_id": document_id}).sort("created_at", -1)
    
    comments = []
    async for comment_doc in cursor:
        comments.append(Comment.from_db(CommentInDB(**comment_doc)))
    
    return comments

@router.put("/{comment_id}", response_model=Comment)
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update a comment"""
    db = await get_database()
    
    try:
        update_data = {k: v for k, v in comment_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db["comments"].update_one(
            {
                "_id": ObjectId(comment_id),
                "user_id": current_user.id
            },
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        updated_comment = await db["comments"].find_one({"_id": ObjectId(comment_id)})
        return Comment.from_db(CommentInDB(**updated_comment))
    except Exception as e:
        logger.error(f"Error updating comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment"""
    db = await get_database()
    
    try:
        result = await db["comments"].delete_one({
            "_id": ObjectId(comment_id),
            "user_id": current_user.id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return {"message": "Comment deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )

@router.put("/{comment_id}/resolve")
async def resolve_comment(
    comment_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Resolve a comment"""
    db = await get_database()
    
    try:
        result = await db["comments"].update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {"resolved": True, "updated_at": datetime.utcnow()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return {"message": "Comment resolved successfully"}
    except Exception as e:
        logger.error(f"Error resolving comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve comment"
        )