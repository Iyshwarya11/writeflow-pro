from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class ReadabilityAnalysis(BaseModel):
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    automated_readability_index: float
    coleman_liau_index: float
    gunning_fog: float
    smog_index: float
    overall_score: float

class ToneAnalysis(BaseModel):
    formal: float
    confident: float
    optimistic: float
    analytical: float
    friendly: float
    assertive: float

class WritingStats(BaseModel):
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_sentence_length: float
    avg_word_length: float
    passive_voice_percentage: float
    adverb_percentage: float
    vocabulary_diversity: float
    reading_time: int

class DocumentAnalytics(BaseModel):
    document_id: str
    readability: ReadabilityAnalysis
    tone: ToneAnalysis
    stats: WritingStats
    plagiarism_score: float
    suggestions_count: Dict[str, int]
    generated_at: datetime

class KeywordExtraction(BaseModel):
    keywords: List[Dict[str, float]]  # keyword: score
    entities: List[Dict[str, str]]    # entity: type
    topics: List[str]

class UserStats(BaseModel):
    total_documents: int
    total_words_written: int
    avg_writing_score: float
    most_used_writing_goal: str
    productivity_trend: List[Dict[str, int]]  # date: word_count
    improvement_areas: List[str]