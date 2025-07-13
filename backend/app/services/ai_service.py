import re
import nltk
import textstat
from groq import Groq
from typing import List, Dict, Any, Optional
from app.config import settings
from app.models.suggestion import Suggestion, SuggestionCreate, SuggestionPosition
from app.models.analytics import ToneAnalysis, ReadabilityAnalysis, WritingStats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ------------------------------
# NLTK Setup
# ------------------------------
def ensure_nltk_data():
    for pkg in ['punkt', 'stopwords']:
        try:
            nltk.data.find(f'tokenizers/{pkg}' if pkg == 'punkt' else f'corpora/{pkg}')
        except LookupError:
            nltk.download(pkg)


# ------------------------------
# AI Service Class
# ------------------------------
class AIService:
    def __init__(self):
        ensure_nltk_data()
        self.groq_client = None
        if settings.groq_api_key and settings.groq_api_key.strip():
            try:
                self.groq_client = Groq(api_key=settings.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")

    async def generate_suggestions(
        self, 
        content: str, 
        document_id: str, 
        user_id: str,
        writing_goal: str = "professional",
        language: str = "en-US"
    ) -> List[Suggestion]:
        suggestions = []
        suggestions.extend(self._check_grammar(content, document_id, user_id))
        suggestions.extend(self._check_style(content, document_id, user_id, writing_goal))
        suggestions.extend(self._check_clarity(content, document_id, user_id))
        suggestions.extend(self._check_vocabulary(content, document_id, user_id))

        if self.groq_client:
            try:
                ai_suggestions = await self._get_groq_suggestions(content, document_id, user_id, writing_goal)
                suggestions.extend(ai_suggestions)
            except Exception as e:
                logger.error(f"Groq API error: {e}")

        return suggestions[:20]

    def _check_grammar(self, content, document_id, user_id):
        patterns = [
            (r'\b(there|their|they\'re)\b', 'Check there/their/they\'re usage'),
            (r'\b(your|you\'re)\b', 'Check your/you\'re usage'),
            (r'\b(its|it\'s)\b', 'Check its/it\'s usage'),
            (r'\s{2,}', 'Multiple spaces found'),
            (r'[.!?]{2,}', 'Multiple punctuation marks')
        ]
        suggestions = []
        for i, (pattern, explanation) in enumerate(patterns):
            for match in re.finditer(pattern, content, re.IGNORECASE):
                suggestions.append(Suggestion(
                    id=f"grammar_{i}_{match.start()}",
                    document_id=document_id,
                    user_id=user_id,
                    type="grammar",
                    text=match.group(),
                    suggestion=match.group().strip(),
                    explanation=explanation,
                    position=SuggestionPosition(start=match.start(), end=match.end()),
                    severity="warning",
                    confidence=75.0,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                ))
        return suggestions

    def _check_style(self, content, document_id, user_id, writing_goal):
        suggestions = []
        passive_patterns = [r'\b(was|were|is|are|been|being)\s+\w+ed\b', r'\b(was|were|is|are|been|being)\s+\w+en\b']
        for pattern in passive_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                suggestions.append(Suggestion(
                    id=f"style_passive_{match.start()}",
                    document_id=document_id,
                    user_id=user_id,
                    type="style",
                    text=match.group(),
                    suggestion="Consider active voice",
                    explanation="Active voice is often more engaging and direct",
                    position=SuggestionPosition(start=match.start(), end=match.end()),
                    severity="info",
                    confidence=60.0,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                ))
        return suggestions[:5]

    def _check_clarity(self, content, document_id, user_id):
        suggestions = []
        sentences = nltk.sent_tokenize(content, language="english")
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) > 25:
                start = content.find(sentence)
                suggestions.append(Suggestion(
                    id=f"clarity_long_{i}",
                    document_id=document_id,
                    user_id=user_id,
                    type="clarity",
                    text=sentence[:50] + "..." if len(sentence) > 50 else sentence,
                    suggestion="Consider breaking into shorter sentences",
                    explanation=f"This sentence has {len(sentence.split())} words.",
                    position=SuggestionPosition(start=start, end=start + len(sentence)),
                    severity="info",
                    confidence=70.0,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                ))
        return suggestions[:3]

    def _check_vocabulary(self, content, document_id, user_id):
        suggestions = []
        replacements = {
            'very good': 'excellent',
            'very bad': 'terrible',
            'very big': 'enormous',
            'very small': 'tiny',
            'a lot of': 'many',
            'thing': 'item/matter/subject'
        }
        for original, replacement in replacements.items():
            pattern = r'\b' + re.escape(original) + r'\b'
            for match in re.finditer(pattern, content, re.IGNORECASE):
                suggestions.append(Suggestion(
                    id=f"vocab_{hash(original)}_{match.start()}",
                    document_id=document_id,
                    user_id=user_id,
                    type="vocabulary",
                    text=match.group(),
                    suggestion=replacement,
                    explanation=f"Consider using '{replacement}'",
                    position=SuggestionPosition(start=match.start(), end=match.end()),
                    severity="info",
                    confidence=80.0,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                ))
        return suggestions[:5]

    async def _get_groq_suggestions(self, content, document_id, user_id, writing_goal):
        if not self.groq_client:
            return []
        prompt = f"""
        You are an expert writing assistant. Analyze the following text for writing improvements based on the goal: {writing_goal}.
        Provide up to 5 actionable suggestions in this format:
        - Type:
        - Issue:
        - Suggestion:
        - Explanation:
        Text: {content[:2000]}
        """
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=1000,
            temperature=0.2
        )
        return self._parse_groq_response(response.choices[0].message.content, document_id, user_id, content)

    def _parse_groq_response(self, ai_text, document_id, user_id, content):
        suggestions = []
        lines = ai_text.split('\n')
        current = {}
        for line in lines:
            if line.startswith('- Type:'):
                if current: suggestions.append(self._create_suggestion_from_parsed(current, document_id, user_id, content))
                current = {'type': line.split(':',1)[1].strip()}
            elif line.startswith('- Issue:'):
                current['issue'] = line.split(':',1)[1].strip()
            elif line.startswith('- Suggestion:'):
                current['suggestion'] = line.split(':',1)[1].strip()
            elif line.startswith('- Explanation:'):
                current['explanation'] = line.split(':',1)[1].strip()
        if current:
            suggestions.append(self._create_suggestion_from_parsed(current, document_id, user_id, content))
        return [s for s in suggestions if s]

    def _create_suggestion_from_parsed(self, parsed, document_id, user_id, content):
        if not all(k in parsed for k in ('type', 'issue', 'suggestion', 'explanation')):
            return None
        issue_text = parsed['issue'].strip('"[]')
        start = content.lower().find(issue_text.lower())
        end = start + len(issue_text) if start >= 0 else min(50, len(content))
        if start < 0: start = 0
        severity = {'grammar': 'error', 'style': 'warning', 'clarity': 'info', 'tone': 'info', 'vocabulary': 'info'}.get(parsed['type'], 'info')
        return Suggestion(
            id=f"groq_{parsed['type']}_{start}_{hash(parsed['issue'])}",
            document_id=document_id,
            user_id=user_id,
            type=parsed['type'],
            text=issue_text,
            suggestion=parsed['suggestion'],
            explanation=parsed['explanation'],
            position=SuggestionPosition(start=start, end=end),
            severity=severity,
            confidence=90.0,
            is_applied=False,
            is_dismissed=False,
            created_at=datetime.utcnow()
        )

    def analyze_tone(self, content: str) -> ToneAnalysis:
        formal_words = ['therefore', 'furthermore', 'consequently', 'moreover']
        confident_words = ['will', 'definitely', 'certainly']
        optimistic_words = ['excellent', 'great', 'wonderful']
        analytical_words = ['analyze', 'evaluate', 'assess']
        word_count = len(content.split())
        scale = max(word_count / 100, 1)
        return ToneAnalysis(
            formal=min(sum(w in content.lower() for w in formal_words)/scale*100, 100),
            confident=min(sum(w in content.lower() for w in confident_words)/scale*100, 100),
            optimistic=min(sum(w in content.lower() for w in optimistic_words)/scale*100, 100),
            analytical=min(sum(w in content.lower() for w in analytical_words)/scale*100, 100),
            friendly=70.0,
            assertive=65.0
        )

    def analyze_readability(self, content: str) -> ReadabilityAnalysis:
        if not content.strip():
            return ReadabilityAnalysis(**{k: 0 for k in ReadabilityAnalysis.__annotations__})
        try:
            flesch = textstat.flesch_reading_ease(content)
            grade = textstat.flesch_kincaid_grade(content)
            ari = textstat.automated_readability_index(content)
            coleman = textstat.coleman_liau_index(content)
            fog = textstat.gunning_fog(content)
            smog = textstat.smog_index(content)
            score = max(0, min(100, (flesch + (100 - grade * 10)) / 2))
            return ReadabilityAnalysis(
                flesch_reading_ease=flesch,
                flesch_kincaid_grade=grade,
                automated_readability_index=ari,
                coleman_liau_index=coleman,
                gunning_fog=fog,
                smog_index=smog,
                overall_score=score
            )
        except:
            return ReadabilityAnalysis(
                flesch_reading_ease=50,
                flesch_kincaid_grade=8,
                automated_readability_index=8,
                coleman_liau_index=8,
                gunning_fog=8,
                smog_index=8,
                overall_score=50
            )

    def calculate_writing_stats(self, content: str) -> WritingStats:
        if not content.strip():
            return WritingStats(**{k: 0 for k in WritingStats.__annotations__})
        words = content.split()
        sentences = nltk.sent_tokenize(content)
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_word_length = sum(len(w) for w in words) / max(word_count, 1)
        passive = len(re.findall(r'\b(was|were|is|are|been|being)\s+\w+ed\b', content, re.IGNORECASE))
        adverbs = len(re.findall(r'\b\w+ly\b', content, re.IGNORECASE))
        unique = len(set(w.lower() for w in words))
        return WritingStats(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            passive_voice_percentage=passive / max(sentence_count, 1) * 100,
            adverb_percentage=adverbs / max(word_count, 1) * 100,
            vocabulary_diversity=unique / max(word_count, 1) * 100,
            reading_time=max(1, word_count // 200)
        )

    def check_plagiarism(self, content: str) -> float:
        phrases = ["lorem ipsum", "the quick brown fox", "to be or not to be", "it was the best of times"]
        score = sum(10 for phrase in phrases if phrase in content.lower())
        return min(score, 100)


# Global instance
ai_service = AIService()
