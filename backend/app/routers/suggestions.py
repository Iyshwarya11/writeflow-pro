from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.models.suggestion import Suggestion, SuggestionUpdate, SuggestionInDB
from app.models.user import User
from app.services.ai_service import ai_service
from app.services.document_service import document_service
from app.database import get_database
from app.dependencies import get_current_active_user
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai-suggestions"])

class SuggestionRequest(BaseModel):
    document_id: str
    content: str
    writing_goal: str = "professional"
    language: str = "en-US"

class ToneAnalysisRequest(BaseModel):
    content: str

class PlagiarismCheckRequest(BaseModel):
    content: str

@router.post("/suggestions", response_model=List[Suggestion])
async def generate_suggestions(
    request: SuggestionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI suggestions for a document"""
    try:
        # Verify document ownership if document exists
        if request.document_id != "temp":
            document = await document_service.get_document(request.document_id, current_user.id)
            if not document:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found"
                )
        
        # Generate suggestions
        suggestions = await ai_service.generate_suggestions(
            content=request.content,
            document_id=request.document_id,
            user_id=current_user.id,
            writing_goal=request.writing_goal,
            language=request.language
        )
        
        # Store suggestions in database (only for real documents)
        if request.document_id != "temp" and suggestions:
            db = await get_database()
            suggestion_docs = []
            for suggestion in suggestions:
                suggestion_in_db = SuggestionInDB(
                    document_id=suggestion.document_id,
                    user_id=suggestion.user_id,
                    type=suggestion.type,
                    text=suggestion.text,
                    suggestion=suggestion.suggestion,
                    explanation=suggestion.explanation,
                    position=suggestion.position,
                    severity=suggestion.severity,
                    confidence=suggestion.confidence,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                )
                suggestion_docs.append(suggestion_in_db.dict(by_alias=True))
            
            await db["suggestions"].insert_many(suggestion_docs)
        
        return suggestions
    except Exception as e:
        logger.error(f"Error generating suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate suggestions"
        )

@router.get("/suggestions/{document_id}", response_model=List[Suggestion])
async def get_document_suggestions(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get all suggestions for a document"""
    # Verify document ownership
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db = await get_database()
    cursor = db["suggestions"].find({
        "document_id": document_id,
        "user_id": current_user.id,
        "is_dismissed": False
    }).sort("created_at", -1)
    
    suggestions = []
    async for suggestion_doc in cursor:
        # Convert from database format to response format
        suggestion_in_db = SuggestionInDB(**suggestion_doc)
        suggestion = Suggestion.from_db(suggestion_in_db)
        suggestions.append(suggestion)
    
    return suggestions

@router.put("/suggestions/{suggestion_id}/apply")
async def apply_suggestion(
    suggestion_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Apply a suggestion"""
    db = await get_database()
    
    result = await db["suggestions"].update_one(
        {
            "_id": ObjectId(suggestion_id),
            "user_id": current_user.id
        },
        {"$set": {"is_applied": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    return {"message": "Suggestion applied successfully"}

@router.put("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(
    suggestion_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Dismiss a suggestion"""
    db = await get_database()
    
    result = await db["suggestions"].update_one(
        {
            "_id": ObjectId(suggestion_id),
            "user_id": current_user.id
        },
        {"$set": {"is_dismissed": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    return {"message": "Suggestion dismissed successfully"}

@router.post("/tone-analysis")
async def analyze_tone(
    request: ToneAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze the tone of text"""
    try:
        tone_analysis = ai_service.analyze_tone(request.content)
        return tone_analysis
    except Exception as e:
        logger.error(f"Error analyzing tone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze tone"
        )

@router.post("/plagiarism-check")
async def check_plagiarism(
    request: PlagiarismCheckRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Check text for plagiarism"""
    try:
        plagiarism_score = ai_service.check_plagiarism(request.content)
        return {
            "plagiarism_score": plagiarism_score,
            "status": "original" if plagiarism_score < 5 else "similarities_found"
        }
    except Exception as e:
        logger.error(f"Error checking plagiarism: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check plagiarism"
        )

@router.post("/vocabulary-enhancement")
async def enhance_vocabulary(
    request: ToneAnalysisRequest,  # Reuse the same request model
    current_user: User = Depends(get_current_active_user)
):
    """Get vocabulary enhancement suggestions"""
    try:
        # Generate vocabulary-specific suggestions
        suggestions = await ai_service.generate_suggestions(
            content=request.content,
            document_id="temp",  # Temporary ID for vocabulary suggestions
            user_id=current_user.id,
            writing_goal="vocabulary",
            language="en-US"
        )
        
        # Filter only vocabulary suggestions
        vocab_suggestions = [s for s in suggestions if s.type == "vocabulary"]
        return vocab_suggestions
    except Exception as e:
        logger.error(f"Error enhancing vocabulary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enhance vocabulary"
        )