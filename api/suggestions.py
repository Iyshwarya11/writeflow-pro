# FastAPI Backend - Suggestions API (Fixed for offline/network issues)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import re
import random
from datetime import datetime

app = FastAPI()

class TextInput(BaseModel):
    content: str
    goal: Optional[str] = "clarity"

class Suggestion(BaseModel):
    id: str
    type: str
    text: str
    suggestion: str
    explanation: str
    position: dict

class SuggestionResponse(BaseModel):
    suggestions: List[Suggestion]
    stats: dict

@app.post("/api/suggestions", response_model=SuggestionResponse)
async def get_suggestions(text_input: TextInput):
    """
    Get writing suggestions using rule-based analysis (no external models required)
    """
    try:
        content = text_input.content
        goal = text_input.goal
        
        # Get suggestions using rule-based approach
        suggestions = []
        suggestions.extend(check_grammar_rules(content))
        suggestions.extend(check_clarity_issues(content))
        suggestions.extend(check_tone_issues(content))
        suggestions.extend(check_engagement_issues(content))
        
        # Calculate statistics
        stats = calculate_stats(content)
        
        return SuggestionResponse(
            suggestions=suggestions,
            stats=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def check_grammar_rules(text: str) -> List[Suggestion]:
    """Check grammar using rule-based approach"""
    suggestions = []
    
    # Common grammar patterns
    patterns = [
        {
            "pattern": r"\bthere\s+is\s+\w+\s+\w+s\b",
            "type": "grammar",
            "suggestion": "Use 'there are' with plural nouns",
            "explanation": "Subject-verb agreement error"
        },
        {
            "pattern": r"\bits\s+\w+ing\b",
            "type": "grammar", 
            "suggestion": "Consider 'it's' (it is) instead of 'its' (possessive)",
            "explanation": "Common its/it's confusion"
        },
        {
            "pattern": r"\byour\s+\w+ing\b",
            "type": "grammar",
            "suggestion": "Consider 'you're' (you are) instead of 'your' (possessive)",
            "explanation": "Common your/you're confusion"
        },
        {
            "pattern": r"\b(very|really|quite|extremely)\s+\w+",
            "type": "clarity",
            "suggestion": "Consider using a stronger adjective instead of intensifiers",
            "explanation": "Intensifiers can weaken your writing"
        }
    ]
    
    for i, pattern_info in enumerate(patterns):
        matches = re.finditer(pattern_info["pattern"], text, re.IGNORECASE)
        for match in matches:
            suggestions.append(Suggestion(
                id=f"grammar_{i}_{match.start()}",
                type=pattern_info["type"],
                text=match.group(),
                suggestion=pattern_info["suggestion"],
                explanation=pattern_info["explanation"],
                position={"start": match.start(), "end": match.end()}
            ))
    
    return suggestions

def check_clarity_issues(text: str) -> List[Suggestion]:
    """Check for clarity issues"""
    suggestions = []
    
    # Long sentences
    sentences = re.split(r'[.!?]+', text)
    for i, sentence in enumerate(sentences):
        words = sentence.split()
        if len(words) > 25:
            start_pos = text.find(sentence.strip())
            if start_pos != -1:
                suggestions.append(Suggestion(
                    id=f"clarity_long_{i}",
                    type="clarity",
                    text=sentence.strip()[:50] + "...",
                    suggestion="Consider breaking this into shorter sentences",
                    explanation="Long sentences can be hard to follow",
                    position={"start": start_pos, "end": start_pos + len(sentence)}
                ))
    
    # Passive voice detection
    passive_patterns = [
        r"\b(was|were|is|are|been|being)\s+\w+ed\b",
        r"\b(was|were|is|are|been|being)\s+\w+en\b"
    ]
    
    for pattern in passive_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            suggestions.append(Suggestion(
                id=f"clarity_passive_{match.start()}",
                type="clarity",
                text=match.group(),
                suggestion="Consider using active voice",
                explanation="Active voice is more direct and engaging",
                position={"start": match.start(), "end": match.end()}
            ))
    
    return suggestions

def check_tone_issues(text: str) -> List[Suggestion]:
    """Check for tone issues"""
    suggestions = []
    
    # Weak words
    weak_words = ["maybe", "perhaps", "possibly", "might", "could", "sort of", "kind of"]
    
    for weak_word in weak_words:
        pattern = r'\b' + re.escape(weak_word) + r'\b'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            suggestions.append(Suggestion(
                id=f"tone_weak_{match.start()}",
                type="tone",
                text=match.group(),
                suggestion="Consider using more confident language",
                explanation="Weak words can undermine your authority",
                position={"start": match.start(), "end": match.end()}
            ))
    
    return suggestions

def check_engagement_issues(text: str) -> List[Suggestion]:
    """Check for engagement issues"""
    suggestions = []
    
    # Repetitive sentence starters
    sentences = re.split(r'[.!?]+', text)
    starters = {}
    
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            first_words = ' '.join(sentence.split()[:2]).lower()
            if first_words in starters:
                starters[first_words] += 1
            else:
                starters[first_words] = 1
    
    for starter, count in starters.items():
        if count > 2:
            suggestions.append(Suggestion(
                id=f"engagement_repetitive_{starter}",
                type="engagement",
                text=f"Sentences starting with '{starter}'",
                suggestion="Vary your sentence beginnings",
                explanation="Repetitive sentence starters can make writing monotonous",
                position={"start": 0, "end": 50}
            ))
    
    return suggestions

def calculate_stats(text: str) -> dict:
    """Calculate text statistics"""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    paragraphs = text.split('\n\n')
    
    # Simple readability score based on sentence and word length
    avg_sentence_length = len(words) / max(1, len([s for s in sentences if s.strip()]))
    avg_word_length = sum(len(word) for word in words) / max(1, len(words))
    
    # Simple readability formula (higher is better)
    readability_score = max(0, min(100, 100 - (avg_sentence_length * 2) - (avg_word_length * 5)))
    
    return {
        "wordCount": len(words),
        "characters": len(text),
        "sentences": len([s for s in sentences if s.strip()]),
        "paragraphs": len([p for p in paragraphs if p.strip()]),
        "readingTime": max(1, len(words) // 250),
        "readabilityScore": int(readability_score)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)