import os
import json
import re
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Body, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import aiohttp
from database import db_manager  # Import the DatabaseManager instance
from pymongo import ReturnDocument
from datetime import timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Server starting up...")
    await db_manager.connect()
    yield
    logger.info("API Server shutting down...")
    await db_manager.close()

# Create main application
app = FastAPI(
    title="GrammarlyClone AI API",
    description="AI-powered writing assistant with real-time suggestions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class DocumentResponse(BaseModel):
    id: str
    title: str
    content: str
    word_count: int
    score: int
    status: str
    last_modified: str
    created_at: str

class DashboardStats(BaseModel):
    words_written: int
    documents_created: int
    average_score: int
    improvement_rate: int

class RecentDocument(BaseModel):
    id: str
    title: str
    last_modified: str
    word_count: int
    score: int
    status: str
# Pydantic models

class DocumentCreate(BaseModel):
    title: str
    content: str
    user_id: str = "default"

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class AITextInput(BaseModel):
    content: str
    goal: Optional[str] = "clarity"
    tone: Optional[str] = "professional"
    audience: Optional[str] = "general"

class AISuggestion(BaseModel):
    id: str
    type: str
    category: str
    original_text: str
    suggested_text: str
    explanation: str
    confidence: float
    position: Dict[str, int]
    severity: str  # low, medium, high
    rule: Optional[str] = None  # Grammar rule or writing principle

class AIAnalytics(BaseModel):
    readability_score: float
    sentiment_score: float
    tone_analysis: Dict[str, float]
    complexity_score: float
    engagement_score: float
    word_diversity: float
    sentence_variety: float

class AISuggestionResponse(BaseModel):
    suggestions: List[AISuggestion]
    analytics: AIAnalytics
    stats: Dict[str, Any]
    processing_time: float

class PlagiarismRequest(BaseModel):
    content: str
    check_web: bool = True
    check_academic: bool = True

class PlagiarismMatch(BaseModel):
    id: str
    source: str
    similarity: float
    matched_text: str
    source_text: str
    url: str
    type: str
    confidence: float

class PlagiarismResponse(BaseModel):
    overall_score: float
    risk_level: str
    matches: List[PlagiarismMatch]
    processing_time: float
    sources_checked: int

class InsightRequest(BaseModel):
    user_id: str
    time_range: str = "week"  # week, month, year

class WritingInsight(BaseModel):
    type: str
    title: str
    description: str
    impact: str
    recommendation: str

class InsightResponse(BaseModel):
    insights: List[WritingInsight]
    performance_metrics: Dict[str, Any]
    improvement_areas: List[str]
    achievements: List[Dict[str, Any]]
    activity_chart: List[Dict[str, Any]]

class RewriteRequest(BaseModel):
    content: str
    goal: str = "formal"

class RewriteResponse(BaseModel):
    rewritten_text: str

class SummarizeRequest(BaseModel):
    content: str

class SummarizeResponse(BaseModel):
    summary: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "openai_api": "available" if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here" else "not_configured",
            "mongodb": "available"
        }
    }

async def analyze_text_with_ai(content: str) -> AIAnalytics:
    """Analyze text using AI for various metrics"""
    try:
        # Calculate basic metrics
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        # Readability score (simplified Flesch Reading Ease)
        if sentences and words:
            avg_sentence_length = len(words) / len(sentences)
            readability_score = max(0, min(100, 100 - (avg_sentence_length * 1.5)))
        else:
            readability_score = 50
        # Sentiment analysis (simplified)
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
        positive_count = sum(1 for word in words if word.lower() in positive_words)
        negative_count = sum(1 for word in words if word.lower() in negative_words)
        if words:
            sentiment_score = (positive_count - negative_count) / len(words) * 100
        else:
            sentiment_score = 0
        # Tone analysis
        formal_words = ["therefore", "furthermore", "consequently", "utilize", "facilitate"]
        informal_words = ["gonna", "wanna", "gotta", "cool", "awesome"]
        formal_count = sum(1 for word in words if word.lower() in formal_words)
        informal_count = sum(1 for word in words if word.lower() in informal_words)
        tone_analysis = {
            "formal": formal_count / max(len(words), 1) * 100,
            "informal": informal_count / max(len(words), 1) * 100,
            "neutral": 100 - (formal_count + informal_count) / max(len(words), 1) * 100
        }
        # Complexity score
        unique_words = len(set(words))
        complexity_score = (unique_words / max(len(words), 1)) * 100
        # Engagement score
        question_count = content.count('?')
        exclamation_count = content.count('!')
        engagement_score = min(100, (question_count + exclamation_count) * 10)
        # Word diversity
        word_diversity = (unique_words / max(len(words), 1)) * 100
        # Sentence variety
        sentence_lengths = [len(s.split()) for s in sentences]
        if sentence_lengths:
            sentence_variety = (max(sentence_lengths) - min(sentence_lengths)) / max(max(sentence_lengths), 1) * 100
        else:
            sentence_variety = 0
        return AIAnalytics(
            readability_score=readability_score,
            sentiment_score=sentiment_score,
            tone_analysis=tone_analysis,
            complexity_score=complexity_score,
            engagement_score=engagement_score,
            word_diversity=word_diversity,
            sentence_variety=sentence_variety
        )
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return AIAnalytics(
            readability_score=50,
            sentiment_score=0,
            tone_analysis={"formal": 0, "informal": 0, "neutral": 100},
            complexity_score=50,
            engagement_score=0,
            word_diversity=50,
            sentence_variety=0
        )

def calculate_text_stats(content: str) -> Dict[str, Any]:
    """Calculate basic text statistics"""
    words = content.split()
    sentences = re.split(r'[.!?]+', content)
    sentences = [s.strip() for s in sentences if s.strip()]
    return {
        "word_count": len(words),
        "character_count": len(content),
        "sentence_count": len(sentences),
        "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
        "average_words_per_sentence": len(words) / max(len(sentences), 1),
        "reading_time_minutes": len(words) / 200,  # Average reading speed
        "unique_words": len(set(words)),
        "vocabulary_diversity": len(set(words)) / max(len(words), 1)
    }

# Document management endpoints
@app.post("/api/documents")
async def create_document(document: DocumentCreate):
    """Create a new document"""
    try:
        logger.info(f"Received request to create document: {document}")
        analytics = await analyze_text_with_ai(document.content)
        score = calculate_document_score(analytics)
        logger.info(f"Calculated score for document: {score}")
        doc_id = await db_manager.save_document(document.user_id, document.title, document.content, score)
        logger.info(f"Saving document with score: {score}")
        await db_manager.save_suggestions(doc_id, [])  # Placeholder for suggestions if needed
        logger.info(f"Document created in MongoDB with id: {doc_id}")
        return {
            "document_id": doc_id, 
            "message": "Document created successfully", 
            "score": score,
            "analytics": analytics.dict() if hasattr(analytics, 'dict') else analytics
        }
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@app.get("/api/documents")
async def get_documents(user_id: str = "default", limit: int = 10):
    """Get all documents for a user"""
    try:
        docs = await db_manager.get_user_documents(user_id, limit)
        return [DocumentResponse(
            id=str(doc.get("_id", doc.get("id"))),
            title=doc["title"],
            content=doc["content"],
            word_count=doc["word_count"],
            score=doc.get("score", 0),
            status=doc.get("status", "In Progress"),
            last_modified=str(doc.get("last_modified", "")),
            created_at=str(doc.get("created_at", ""))
        ) for doc in docs]
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document and update last_modified to now for history tracking"""
    try:
        doc = await db_manager.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return DocumentResponse(
            id=str(doc.get("_id", doc.get("id"))),
            title=doc["title"],
            content=doc["content"],
            word_count=doc["word_count"],
            score=doc.get("score", 0),
            status=doc.get("status", "In Progress"),
            last_modified=str(doc.get("last_modified", "")),
            created_at=str(doc.get("created_at", ""))
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")

@app.put("/api/documents/{document_id}")
async def update_document(document_id: str, document: DocumentUpdate):
    """Update a document"""
    try:
        doc = await db_manager.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        title = document.title if document.title is not None else doc["title"]
        content = document.content if document.content is not None else doc["content"]
        await db_manager.save_document(doc["user_id"], title, content, document_id=document_id)
        updated_doc = await db_manager.get_document(document_id)
        return DocumentResponse(
            id=str(updated_doc.get("_id", updated_doc.get("id"))),
            title=updated_doc["title"],
            content=updated_doc["content"],
            word_count=updated_doc["word_count"],
            score=updated_doc.get("score", 0),
            status=updated_doc.get("status", "In Progress"),
            last_modified=str(updated_doc.get("last_modified", "")),
            created_at=str(updated_doc.get("created_at", ""))
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update document")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        await db_manager.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

# AI Suggestions endpoint (OpenAI only)
async def openai_chat_completion(prompt: str, max_tokens: int = 800, temperature: float = 0.3) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=20) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
            else:
                text = await response.text()
                logger.error(f"OpenAI API error: {response.status} {text}")
                raise HTTPException(status_code=500, detail="OpenAI API error")

@app.post("/api/ai/suggestions", response_model=AISuggestionResponse)
async def get_ai_suggestions(text_input: AITextInput):
    start_time = datetime.now()
    try:
        prompt = (
            f"You are a professional writing assistant. Analyze the following text and provide comprehensive writing suggestions to improve {text_input.goal} for a {text_input.tone} tone targeting {text_input.audience} audience.\n\nText: \"{text_input.content}\"\n\nRespond ONLY with a valid JSON object in the following format:\n{{\n  \"suggestions\": [\n    {{\n      \"type\": \"spelling|grammar|clarity|tone|engagement|style|punctuation|tense\",\n      \"category\": \"specific category\",\n      \"original_text\": \"exact text to be changed\",\n      \"suggested_text\": \"improved version\",\n      \"explanation\": \"detailed explanation of why this change improves the writing\",\n      \"confidence\": 0.85,\n      \"severity\": \"low|medium|high\"\n    }}\n  ]\n}}\nNO explanation, NO extra text, ONLY the JSON object."
        )
        response_text = await openai_chat_completion(prompt)
        # Fix indentation here
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group(0)
            parsed_response = json.loads(json_str)
            suggestions = []
            for i, suggestion in enumerate(parsed_response.get("suggestions", [])):
                original_text = suggestion.get("original_text", "")
                suggested_text = suggestion.get("suggested_text", "")
                position = {"start": 0, "end": len(original_text)}
                if original_text and original_text in text_input.content:
                    start_pos = text_input.content.find(original_text)
                    if start_pos != -1:
                        position = {"start": start_pos, "end": start_pos + len(original_text)}
                suggestions.append(AISuggestion(
                    id=f"openai_suggestion_{i}",
                    type=suggestion.get("type", "general"),
                    category=suggestion.get("category", "improvement"),
                    original_text=original_text,
                    suggested_text=suggested_text,
                    explanation=suggestion.get("explanation", ""),
                    confidence=suggestion.get("confidence", 0.8),
                    position=position,
                    severity=suggestion.get("severity", "medium")
                ))
        else:
            suggestions = []
        analytics = await analyze_text_with_ai(text_input.content)
        stats = calculate_text_stats(text_input.content)
        processing_time = (datetime.now() - start_time).total_seconds()
        return AISuggestionResponse(
            suggestions=suggestions,
            analytics=analytics,
            stats=stats,
            processing_time=processing_time
        )
    except Exception as e:
        logger.error(f"Error getting AI suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI suggestions")

def calculate_document_score(analytics) -> int:
    """Calculate overall document score from analytics"""
    try:
        if hasattr(analytics, 'dict'):
            analytics_dict = analytics.dict()
        else:
            analytics_dict = analytics
            
        readability = analytics_dict.get("readability_score", 50)
        engagement = analytics_dict.get("engagement_score", 50)
        word_diversity = analytics_dict.get("word_diversity", 50)
        
        # Weighted average
        score = (readability * 0.4 + engagement * 0.3 + word_diversity * 0.3)
        return int(max(0, min(100, score)))
    except:
        return 75  # Default score

async def store_analytics(user_id: str, document_id: str, analytics: AIAnalytics):
    """Store analytics data for a document"""
    try:
        await db_manager.save_analytics(user_id, document_id, analytics)
    except Exception as e:
        logger.error(f"Error storing analytics: {e}")

# Plagiarism check endpoint
@app.post("/api/ai/plagiarism/check", response_model=PlagiarismResponse)
async def check_plagiarism_ai(request: PlagiarismRequest):
    """Check content for plagiarism"""
    start_time = datetime.now()
    
    try:
        matches = []
        
        if request.check_web:
            web_matches = await check_web_sources(request.content)
            matches.extend(web_matches)
        
        if request.check_academic:
            academic_matches = await check_academic_sources(request.content)
            matches.extend(academic_matches)
        
        # Calculate overall similarity score
        if matches:
            overall_score = sum(match.similarity for match in matches) / len(matches)
        else:
            overall_score = 0
        
        # Determine risk level
        if overall_score > 80:
            risk_level = "high"
        elif overall_score > 50:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return PlagiarismResponse(
            overall_score=overall_score,
            risk_level=risk_level,
            matches=matches,
            processing_time=processing_time,
            sources_checked=len(matches)
        )
        
    except Exception as e:
        logger.error(f"Error checking plagiarism: {e}")
        raise HTTPException(status_code=500, detail="Failed to check plagiarism")

async def check_web_sources(content: str) -> List[PlagiarismMatch]:
    """Check web sources for plagiarism (simplified)"""
    matches = []
    # Simulate checking against common phrases
    common_phrases = [
        "The quick brown fox jumps over the lazy dog",
        "To be or not to be, that is the question",
        "All the world's a stage"
    ]
    for i, phrase in enumerate(common_phrases):
        if phrase.lower() in content.lower():
            similarity = len(phrase) / len(content) * 100
            if similarity > 10:  # Only report if similarity is significant
                matches.append(PlagiarismMatch(
                    id=f"web_match_{i}",
                    source="Web Source",
                    similarity=similarity,
                    matched_text=phrase,
                    source_text=phrase,
                    url="https://example.com",
                    type="web",
                    confidence=0.8
                ))
    # Fallback: always return a mock match for any non-empty input
    if not matches and content.strip():
        matches.append(PlagiarismMatch(
            id="web_fallback_0",
            source="Web Source (Mock)",
            similarity=round(min(100, max(10, len(content) % 50 + 10)), 1),
            matched_text=content.strip()[:100] + ("..." if len(content.strip()) > 100 else ""),
            source_text=content.strip()[:100] + ("..." if len(content.strip()) > 100 else ""),
            url="https://example.com/mock",
            type="web",
            confidence=0.5
        ))
    return matches

async def check_academic_sources(content: str) -> List[PlagiarismMatch]:
    """Check academic sources for plagiarism (simplified)"""
    matches = []
    academic_phrases = [
        "The results indicate a significant correlation",
        "Previous research has shown",
        "This study demonstrates"
    ]
    for i, phrase in enumerate(academic_phrases):
        if phrase.lower() in content.lower():
            similarity = len(phrase) / len(content) * 100
            if similarity > 10:
                matches.append(PlagiarismMatch(
                    id=f"academic_match_{i}",
                    source="Academic Database",
                    similarity=similarity,
                    matched_text=phrase,
                    source_text=phrase,
                    url="https://scholar.google.com",
                    type="academic",
                    confidence=0.9
                ))
    # Fallback: always return a mock match for any non-empty input
    if not matches and content.strip():
        matches.append(PlagiarismMatch(
            id="academic_fallback_0",
            source="Academic Source (Mock)",
            similarity=round(min(100, max(10, len(content) % 40 + 10)), 1),
            matched_text=content.strip()[:100] + ("..." if len(content.strip()) > 100 else ""),
            source_text=content.strip()[:100] + ("..." if len(content.strip()) > 100 else ""),
            url="https://scholar.google.com/mock",
            type="academic",
            confidence=0.5
        ))
    return matches

def calculate_similarity_score(text: str) -> float:
    """Calculate similarity score between texts (simplified)"""
    # This is a simplified implementation
    # In production, you would use more sophisticated algorithms
    words = set(text.lower().split())
    return len(words) / max(len(text.split()), 1) * 100

# Writing insights endpoint
@app.post("/api/ai/insights", response_model=InsightResponse)
async def get_writing_insights(request: InsightRequest):
    """Get AI-powered writing insights"""
    try:
        # Get user's documents
        user_docs = await db_manager.get_user_documents(request.user_id, limit=100)
        
        if not user_docs:
            return InsightResponse(
                insights=[],
                performance_metrics={},
                improvement_areas=[],
                achievements=[]
            )
        
        # Generate insights
        insights = await generate_ai_insights(user_docs, request.time_range)
        
        # Calculate performance metrics
        performance_metrics = calculate_performance_metrics(user_docs)

        # Get writing activity and score trend for the last 7 days
        trends = await db_manager.get_writing_trends(request.user_id, days=7)
        # trends: [{_id: {year, month, day}, words, documents}]
        # Map date string to {words, score}
        from collections import defaultdict
        import datetime
        activity_chart = []
        score_map = defaultdict(list)
        for doc in user_docs:
            if doc.get("created_at") and doc.get("score") is not None:
                dt = doc["created_at"]
                if isinstance(dt, str):
                    try:
                        dt = datetime.datetime.fromisoformat(dt)
                    except Exception:
                        continue
                date_str = dt.strftime("%Y-%m-%d")
                score_map[date_str].append(doc.get("score", 0))
        for t in trends:
            d = t["_id"]
            date_str = f"{d['year']}-{d['month']:02d}-{d['day']:02d}"
            avg_score = 0
            if score_map[date_str]:
                avg_score = sum(score_map[date_str]) / len(score_map[date_str])
            activity_chart.append({
                "date": date_str,
                "words": t["words"],
                "score": round(avg_score, 1)
            })
        # Sort by date
        activity_chart.sort(key=lambda x: x["date"])
        
        # Identify improvement areas
        improvement_areas = identify_improvement_areas(user_docs)
        
        # Generate achievements
        achievements = generate_achievements(user_docs)
        
        return InsightResponse(
            insights=insights,
            performance_metrics=performance_metrics,
            improvement_areas=improvement_areas,
            achievements=achievements,
            activity_chart=activity_chart
        )
    except Exception as e:
        logger.error(f"Error getting writing insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get writing insights")

async def generate_ai_insights(documents: List[Dict], time_range: str) -> List[WritingInsight]:
    """Generate AI-powered writing insights"""
    insights = []
    
    if not documents:
        return insights
    
    # Analyze writing patterns
    total_words = sum(doc.get("word_count", 0) for doc in documents)
    avg_score = sum(doc.get("score", 0) for doc in documents) / len(documents)
    
    # Insight 1: Writing volume
    if total_words > 1000:
        insights.append(WritingInsight(
            type="productivity",
            title="High Writing Volume",
            description=f"You've written {total_words} words across {len(documents)} documents.",
            impact="This shows strong writing consistency and dedication to your craft.",
            recommendation="Consider setting daily writing goals to maintain this momentum."
        ))
    
    # Insight 2: Quality improvement
    if avg_score > 80:
        insights.append(WritingInsight(
            type="quality",
            title="Excellent Writing Quality",
            description=f"Your average document score is {avg_score:.1f}/100.",
            impact="Your writing demonstrates high quality and attention to detail.",
            recommendation="Focus on maintaining this high standard while exploring new writing styles."
        ))
    
    # Insight 3: Consistency
    recent_docs = sorted(documents, key=lambda x: x.get("last_modified", ""), reverse=True)[:5]
    if len(recent_docs) >= 3:
        insights.append(WritingInsight(
            type="consistency",
            title="Consistent Writing Habit",
            description="You've been writing regularly with good consistency.",
            impact="Regular writing practice improves skills and builds momentum.",
            recommendation="Try to maintain this consistency and consider daily writing sessions."
        ))
    
    return insights

def calculate_performance_metrics(documents: List[Dict]) -> Dict[str, Any]:
    if not documents:
        return {
            "total_documents": 0,
            "total_words": 0,
            "average_score": 0,
            "writing_frequency": 0,
            "best_score": 0,
            "average_words_per_document": 0,
            "time_spent_per_day": 0
        }
    total_words = sum(doc.get("word_count", 0) for doc in documents)
    avg_score = sum(doc.get("score", 0) for doc in documents) / len(documents) if documents else 0
    best_score = max(doc.get("score", 0) for doc in documents) if documents else 0
    avg_words_per_doc = total_words / len(documents) if documents else 0
    
    # Calculate writing frequency
    dates = []
    for doc in documents:
        value = doc.get("last_modified", "")
        if isinstance(value, datetime):
            value = value.isoformat()
        if isinstance(value, str) and value:
            dates.append(value)
    if dates:
        latest_date = max(dates)
        earliest_date = min(dates)
        days_span = (datetime.fromisoformat(latest_date) - datetime.fromisoformat(earliest_date)).days
        writing_frequency = len(documents) / max(days_span, 1)
    else:
        writing_frequency = 0
    
    # Calculate time spent per day (in minutes)
    from collections import defaultdict
    day_minutes = defaultdict(float)
    for doc in documents:
        created = doc.get("created_at")
        modified = doc.get("last_modified")
        if not created or not modified:
            continue
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created)
            except Exception:
                continue
        if isinstance(modified, str):
            try:
                modified = datetime.fromisoformat(modified)
            except Exception:
                continue
        # Only count if modified is after created
        if modified > created:
            day = modified.date()
            minutes = (modified - created).total_seconds() / 60.0
            day_minutes[day] += minutes
    total_days = len(day_minutes)
    time_spent_per_day = sum(day_minutes.values()) / total_days if total_days > 0 else 0

    return {
        "total_documents": len(documents),
        "total_words": total_words,
        "average_score": round(avg_score, 1),
        "writing_frequency": round(writing_frequency, 2),
        "best_score": best_score,
        "average_words_per_document": avg_words_per_doc,
        "time_spent_per_day": int(time_spent_per_day)
    }

def identify_improvement_areas(documents: List[Dict]) -> List[str]:
    """Identify areas for improvement"""
    areas = []
    
    if not documents:
        return areas
    
    avg_score = sum(doc.get("score", 0) for doc in documents) / len(documents)
    
    if avg_score < 70:
        areas.append("Overall writing quality needs improvement")
    
    word_counts = [doc.get("word_count", 0) for doc in documents]
    avg_words = sum(word_counts) / len(word_counts)
    
    if avg_words < 100:
        areas.append("Consider writing longer, more detailed content")
    
    if len(documents) < 5:
        areas.append("Increase writing frequency for better skill development")
    
    return areas

def generate_achievements(documents: List[Dict]) -> List[Dict[str, Any]]:
    """Generate achievements based on writing performance"""
    achievements = []
    
    if not documents:
        return achievements
    
    total_words = sum(doc.get("word_count", 0) for doc in documents)
    avg_score = sum(doc.get("score", 0) for doc in documents) / len(documents)
    
    # Word count achievements
    if total_words >= 1000:
        achievements.append({
            "title": "Word Warrior",
            "description": f"Wrote {total_words} words",
            "icon": "📝",
            "unlocked": True
        })
    
    if total_words >= 5000:
        achievements.append({
            "title": "Prolific Writer",
            "description": f"Wrote {total_words} words",
            "icon": "✍️",
            "unlocked": True
        })
    
    # Quality achievements
    if avg_score >= 80:
        achievements.append({
            "title": "Quality Master",
            "description": f"Average score: {avg_score:.1f}/100",
            "icon": "🏆",
            "unlocked": True
        })
    
    # Consistency achievements
    if len(documents) >= 10:
            achievements.append({
            "title": "Consistent Writer",
            "description": f"Created {len(documents)} documents",
            "icon": "📚",
            "unlocked": True
            })
    
    return achievements

# User statistics endpoint
@app.get("/api/users/{user_id}/statistics")
async def get_user_statistics(user_id: str, days: int = 7):
    """Get user writing statistics"""
    try:
        # Get user's documents
        user_docs = await db_manager.get_user_documents(user_id)
        if not user_docs:
            return {
                "total_documents": 0,
                "total_words": 0,
                "average_score": 0,
                "writing_streak": 0,
                "recent_activity": [],
                "improvement_rate": 0
            }
        # Calculate statistics
        total_documents = len(user_docs)
        total_words = sum(doc.get("word_count", 0) for doc in user_docs)
        average_score = sum(doc.get("score", 0) for doc in user_docs) / len(user_docs)
        from datetime import datetime, timedelta
        # Calculate writing streak
        dates = [datetime.fromisoformat(doc.get("last_modified", "")) for doc in user_docs if doc.get("last_modified", "")]
        dates.sort(reverse=True)
        streak = 0
        current_date = datetime.now().date()
        for date in dates:
            if date.date() == current_date - timedelta(days=streak):
                streak += 1
            else:
                break
        # Recent activity
        recent_activity = []
        for doc in sorted(user_docs, key=lambda x: x.get("last_modified", ""), reverse=True)[:5]:
            recent_activity.append({
                "title": doc.get("title", ""),
                "word_count": doc.get("word_count", 0),
                "score": doc.get("score", 0),
                "date": doc.get("last_modified", "")
            })
        # Improvement rate: percent change in words written this week vs last week
        this_week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).date()
        last_week_start = this_week_start - timedelta(days=7)
        this_week_words = 0
        last_week_words = 0
        for doc in user_docs:
            lm = doc.get("last_modified", "")
            if not lm:
                continue
            try:
                lm_date = datetime.fromisoformat(lm).date()
            except Exception:
                continue
            if this_week_start <= lm_date <= this_week_start + timedelta(days=6):
                this_week_words += doc.get("word_count", 0)
            elif last_week_start <= lm_date < this_week_start:
                last_week_words += doc.get("word_count", 0)
        improvement_rate = 0
        if last_week_words > 0:
            improvement_rate = round(((this_week_words - last_week_words) / last_week_words) * 100, 1)
        elif this_week_words > 0:
            improvement_rate = 100
        return {
            "total_documents": total_documents,
            "total_words": total_words,
            "average_score": round(average_score, 1),
            "writing_streak": streak,
            "recent_activity": recent_activity,
            "improvement_rate": improvement_rate
        }
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        return {
            "total_documents": 0,
            "total_words": 0,
            "average_score": 0,
            "writing_streak": 0,
            "recent_activity": [],
            "improvement_rate": 0
        }

def analyze_grammar_context(content: str, word: str, position: int) -> str:
    """Analyze grammar context around a word"""
    # This is a simplified implementation
    # In production, you would use more sophisticated NLP libraries
    words = content.split()
    if position < len(words):
        word_at_position = words[position]
        if word_at_position.lower() == word.lower():
            # Basic context analysis
            if position > 0:
                prev_word = words[position - 1]
                if prev_word.lower() in ["a", "an", "the"]:
                    return f"Article '{prev_word}' suggests this should be a noun"
            if position < len(words) - 1:
                next_word = words[position + 1]
                if next_word.lower().endswith("ing"):
                    return f"Following word '{next_word}' suggests this should be a verb"
    return "Context analysis not available"

@app.post("/api/ai/rewrite", response_model=RewriteResponse)
async def rewrite_text(request: RewriteRequest):
    try:
        prompt = f"Rewrite the following text to be more {request.goal}.\n\nText: \"{request.content}\"\n\nRewritten ({request.goal}):"
        rewritten = await openai_chat_completion(prompt)
        return RewriteResponse(rewritten_text=rewritten)
    except Exception as e:
        logger.error(f"Error rewriting text: {e}")
        return RewriteResponse(rewritten_text=request.content)

@app.post("/api/ai/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    try:
        prompt = f"Please provide a concise summary of the following text in no more than 100 words:\n\nText: \"{request.content}\"\n\nSummary:"
        summary = await openai_chat_completion(prompt, max_tokens=200)
        return SummarizeResponse(summary=summary)
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return SummarizeResponse(summary="Summary not available.")

# --- User management endpoints ---
from motor.motor_asyncio import AsyncIOMotorClient

# Ensure users collection exists
mongo_client = None
users_collection = None

def get_users_collection():
    global mongo_client, users_collection
    if users_collection is None:
        mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
        db = mongo_client["grammarly_clone"]
        users_collection = db["users"]
    return users_collection

@app.post("/api/users/upsert")
async def upsert_user(user: dict):
    """Upsert user on login/signup"""
    logger.info(f"Received request to upsert user: {user}")
    extra_fields = {k: v for k, v in user.items() if k != "email"}
    user_doc = await db_manager.upsert_user(user["email"], extra_fields)
    logger.info(f"User upserted in MongoDB: {user_doc}")
    return {"ok": True, "user": user_doc}

@app.get("/api/users/{user_id}")
async def get_user_profile(user_id: str):
    """Get user profile and stats"""
    user = await db_manager.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Get stats
    docs = await db_manager.get_user_documents(user_id)
    stats = calculate_performance_metrics(docs)
    user_profile = {k: v for k, v in user.items() if k != "_id"}
    user_profile["stats"] = stats
    return user_profile

@app.post("/api/admin/fix_user_documents")
async def fix_user_documents(user_id: str = Body(...)):
    """Admin endpoint: Set user_id for all documents missing or with a different user_id to the given user_id (for migration/fix)."""
    from motor.motor_asyncio import AsyncIOMotorClient
    mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    db = mongo_client["grammarly_clone"]
    # Only update documents missing user_id or with a different user_id
    result = await db["documents"].update_many({"$or": [{"user_id": {"$exists": False}}, {"user_id": {"$ne": user_id}}]}, {"$set": {"user_id": user_id}})
    logger.info(f"Admin fix: Set user_id={user_id} for {result.modified_count} documents.")
    return {"ok": True, "modified_count": result.modified_count}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 