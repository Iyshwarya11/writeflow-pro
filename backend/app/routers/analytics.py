from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.models.analytics import DocumentAnalytics, ReadabilityAnalysis, WritingStats, UserStats
from app.models.user import User
from app.services.ai_service import ai_service
from app.services.document_service import document_service
from app.database import get_database
from app.dependencies import get_current_active_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

class AnalyticsRequest(BaseModel):
    content: str

@router.get("/document/{document_id}", response_model=DocumentAnalytics)
async def get_document_analytics(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive analytics for a document"""
    # Verify document ownership
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        # Generate analytics
        readability = ai_service.analyze_readability(document.content)
        tone = ai_service.analyze_tone(document.content)
        stats = ai_service.calculate_writing_stats(document.content)
        plagiarism_score = ai_service.check_plagiarism(document.content)
        
        # Get suggestions count by type
        db = await get_database()
        suggestions_pipeline = [
            {"$match": {"document_id": document_id, "user_id": current_user.id}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        
        suggestions_count = {}
        async for result in db["suggestions"].aggregate(suggestions_pipeline):
            suggestions_count[result["_id"]] = result["count"]
        
        analytics = DocumentAnalytics(
            document_id=document_id,
            readability=readability,
            tone=tone,
            stats=stats,
            plagiarism_score=plagiarism_score,
            suggestions_count=suggestions_count,
            generated_at=datetime.utcnow()
        )
        
        return analytics
    except Exception as e:
        logger.error(f"Error generating document analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics"
        )

@router.get("/document/{document_id}/readability", response_model=ReadabilityAnalysis)
async def get_readability_analysis(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get readability analysis for a document"""
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        return ai_service.analyze_readability(document.content)
    except Exception as e:
        logger.error(f"Error analyzing readability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze readability"
        )

@router.get("/document/{document_id}/keywords")
async def extract_keywords(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Extract keywords from a document"""
    document = await document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    try:
        # Simple keyword extraction (in a real app, use more sophisticated methods)
        words = document.content.lower().split()
        word_freq = {}
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        for word in words:
            word = word.strip('.,!?";()[]{}')
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
            "entities": [],  # Placeholder for named entity recognition
            "topics": []     # Placeholder for topic modeling
        }
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract keywords"
        )

@router.get("/user/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get user writing statistics"""
    try:
        db = await get_database()
        
        # Get user documents
        documents = await document_service.get_user_documents(current_user.id)
        
        total_documents = len(documents)
        total_words = sum(doc.word_count for doc in documents)
        
        # Calculate average writing score (simplified)
        avg_score = 75.0  # Placeholder
        
        # Most used writing goal
        writing_goals = [doc.writing_goal for doc in documents]
        most_used_goal = max(set(writing_goals), key=writing_goals.count) if writing_goals else "professional"
        
        # Productivity trend (last 7 days)
        productivity_trend = []  # Placeholder
        
        # Improvement areas based on suggestions
        suggestions_pipeline = [
            {"$match": {"user_id": current_user.id}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 3}
        ]
        
        improvement_areas = []
        async for result in db["suggestions"].aggregate(suggestions_pipeline):
            improvement_areas.append(result["_id"])
        
        user_stats = UserStats(
            total_documents=total_documents,
            total_words_written=total_words,
            avg_writing_score=avg_score,
            most_used_writing_goal=most_used_goal,
            productivity_trend=productivity_trend,
            improvement_areas=improvement_areas
        )
        
        return user_stats
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )

@router.post("/document/{document_id}/compare")
async def compare_document_versions(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Compare different versions of a document"""
    # This is a placeholder for version comparison functionality
    return {
        "message": "Document version comparison not implemented yet",
        "document_id": document_id
    }