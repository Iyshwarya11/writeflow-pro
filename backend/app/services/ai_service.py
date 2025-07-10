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

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class AIService:
    def __init__(self):
        self.groq_client = None
        if settings.groq_api_key:
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
        """Generate AI-powered writing suggestions"""
        suggestions = []
        
        # Basic suggestions (always available)
        grammar_suggestions = self._check_grammar(content, document_id, user_id)
        suggestions.extend(grammar_suggestions)
        
        style_suggestions = self._check_style(content, document_id, user_id, writing_goal)
        suggestions.extend(style_suggestions)
        
        clarity_suggestions = self._check_clarity(content, document_id, user_id)
        suggestions.extend(clarity_suggestions)
        
        vocab_suggestions = self._check_vocabulary(content, document_id, user_id)
        suggestions.extend(vocab_suggestions)
        
        # Use Groq for advanced suggestions if available
        if self.groq_client and content.strip():
            try:
                ai_suggestions = await self._get_groq_suggestions(
                    content, document_id, user_id, writing_goal
                )
                suggestions.extend(ai_suggestions)
            except Exception as e:
                logger.error(f"Groq API error: {e}")
        
        return suggestions[:20]  # Limit to 20 suggestions
    
    def _check_grammar(self, content: str, document_id: str, user_id: str) -> List[Suggestion]:
        """Basic grammar checking"""
        suggestions = []
        
        # Check for common grammar issues
        patterns = [
            (r'\b(there|their|they\'re)\b', 'Check there/their/they\'re usage'),
            (r'\b(your|you\'re)\b', 'Check your/you\'re usage'),
            (r'\b(its|it\'s)\b', 'Check its/it\'s usage'),
            (r'\s{2,}', 'Multiple spaces found'),
            (r'[.!?]{2,}', 'Multiple punctuation marks'),
        ]
        
        for i, (pattern, explanation) in enumerate(patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                suggestion = Suggestion(
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
                )
                suggestions.append(suggestion)
        
        return suggestions[:5]  # Limit grammar suggestions
    
    def _check_style(self, content: str, document_id: str, user_id: str, writing_goal: str) -> List[Suggestion]:
        """Style checking based on writing goal"""
        suggestions = []
        
        # Passive voice detection
        passive_patterns = [
            r'\b(was|were|is|are|been|being)\s+\w+ed\b',
            r'\b(was|were|is|are|been|being)\s+\w+en\b'
        ]
        
        for pattern in passive_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                suggestion = Suggestion(
                    id=f"style_passive_{match.start()}",
                    document_id=document_id,
                    user_id=user_id,
                    type="style",
                    text=match.group(),
                    suggestion=f"Consider active voice",
                    explanation="Active voice is often more engaging and direct",
                    position=SuggestionPosition(start=match.start(), end=match.end()),
                    severity="info",
                    confidence=60.0,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                )
                suggestions.append(suggestion)
        
        return suggestions[:3]  # Limit style suggestions
    
    def _check_clarity(self, content: str, document_id: str, user_id: str) -> List[Suggestion]:
        """Clarity checking"""
        suggestions = []
        
        # Check for overly long sentences
        sentences = nltk.sent_tokenize(content)
        for i, sentence in enumerate(sentences):
            words = len(sentence.split())
            if words > 25:
                start_pos = content.find(sentence)
                if start_pos != -1:
                    suggestion = Suggestion(
                        id=f"clarity_long_{i}",
                        document_id=document_id,
                        user_id=user_id,
                        type="clarity",
                        text=sentence[:50] + "..." if len(sentence) > 50 else sentence,
                        suggestion="Consider breaking this into shorter sentences",
                        explanation=f"This sentence has {words} words. Shorter sentences improve readability.",
                        position=SuggestionPosition(start=start_pos, end=start_pos + len(sentence)),
                        severity="info",
                        confidence=70.0,
                        is_applied=False,
                        is_dismissed=False,
                        created_at=datetime.utcnow()
                    )
                    suggestions.append(suggestion)
        
        return suggestions[:3]  # Limit clarity suggestions
    
    def _check_vocabulary(self, content: str, document_id: str, user_id: str) -> List[Suggestion]:
        """Vocabulary enhancement suggestions"""
        suggestions = []
        
        # Common word replacements
        replacements = {
            'very good': 'excellent',
            'very bad': 'terrible',
            'very big': 'enormous',
            'very small': 'tiny',
            'a lot of': 'many',
            'thing': 'item/matter/subject',
        }
        
        for original, replacement in replacements.items():
            pattern = r'\b' + re.escape(original) + r'\b'
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                suggestion = Suggestion(
                    id=f"vocab_{hash(original)}_{match.start()}",
                    document_id=document_id,
                    user_id=user_id,
                    type="vocabulary",
                    text=match.group(),
                    suggestion=replacement,
                    explanation=f"Consider using '{replacement}' for more precise language",
                    position=SuggestionPosition(start=match.start(), end=match.end()),
                    severity="info",
                    confidence=80.0,
                    is_applied=False,
                    is_dismissed=False,
                    created_at=datetime.utcnow()
                )
                suggestions.append(suggestion)
        
        return suggestions[:3]  # Limit vocabulary suggestions
    
    async def _get_groq_suggestions(
        self, 
        content: str, 
        document_id: str, 
        user_id: str, 
        writing_goal: str
    ) -> List[Suggestion]:
        """Get advanced suggestions using Groq API"""
        if not self.groq_client:
            return []
        
        try:
            # Limit content length for API efficiency
            content_preview = content[:1500] if len(content) > 1500 else content
            
            prompt = f"""
You are an expert writing assistant. Analyze the following text for writing improvements based on the goal: {writing_goal}.

Provide specific, actionable suggestions in these categories:
1. Grammar errors and corrections
2. Style improvements for {writing_goal} writing
3. Clarity and readability enhancements
4. Tone adjustments
5. Word choice and vocabulary improvements

Text to analyze:
"{content_preview}"

Format each suggestion as:
- Type: [grammar/style/clarity/tone/vocabulary]
- Issue: [specific text with issue]
- Suggestion: [specific improvement]
- Explanation: [why this improves the text]

Provide up to 3 most important suggestions.
"""
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                max_tokens=800,
                temperature=0.2
            )
            
            ai_text = response.choices[0].message.content
            
            # Parse the AI response and create structured suggestions
            suggestions = self._parse_groq_response(ai_text, document_id, user_id, content)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return []
    
    def _parse_groq_response(self, ai_text: str, document_id: str, user_id: str, content: str) -> List[Suggestion]:
        """Parse Groq response into structured suggestions"""
        suggestions = []
        
        try:
            # Split response into individual suggestions
            lines = ai_text.split('\n')
            current_suggestion = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('- Type:'):
                    if current_suggestion and len(current_suggestion) >= 4:
                        # Process previous suggestion
                        suggestion = self._create_suggestion_from_parsed(
                            current_suggestion, document_id, user_id, content
                        )
                        if suggestion:
                            suggestions.append(suggestion)
                    
                    current_suggestion = {'type': line.replace('- Type:', '').strip().lower()}
                elif line.startswith('- Issue:'):
                    current_suggestion['issue'] = line.replace('- Issue:', '').strip()
                elif line.startswith('- Suggestion:'):
                    current_suggestion['suggestion'] = line.replace('- Suggestion:', '').strip()
                elif line.startswith('- Explanation:'):
                    current_suggestion['explanation'] = line.replace('- Explanation:', '').strip()
            
            # Process last suggestion
            if current_suggestion and len(current_suggestion) >= 4:
                suggestion = self._create_suggestion_from_parsed(
                    current_suggestion, document_id, user_id, content
                )
                if suggestion:
                    suggestions.append(suggestion)
                    
        except Exception as e:
            logger.error(f"Error parsing Groq response: {e}")
            # Fallback: create a general suggestion
            suggestion = Suggestion(
                id=f"ai_general_{hash(content[:100])}",
                document_id=document_id,
                user_id=user_id,
                type="style",
                text=content[:100] + "..." if len(content) > 100 else content,
                suggestion="AI-powered improvement available",
                explanation=ai_text[:200] + "..." if len(ai_text) > 200 else ai_text,
                position=SuggestionPosition(start=0, end=min(100, len(content))),
                severity="info",
                confidence=85.0,
                is_applied=False,
                is_dismissed=False,
                created_at=datetime.utcnow()
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def _create_suggestion_from_parsed(self, parsed: dict, document_id: str, user_id: str, content: str) -> Optional[Suggestion]:
        """Create a Suggestion object from parsed data"""
        try:
            if not all(key in parsed for key in ['type', 'issue', 'suggestion', 'explanation']):
                return None
            
            # Find position of the issue in content
            issue_text = parsed['issue'].strip('"[]')
            start_pos = content.lower().find(issue_text.lower())
            
            if start_pos == -1:
                # If exact match not found, use beginning of content
                start_pos = 0
                end_pos = min(50, len(content))
            else:
                end_pos = start_pos + len(issue_text)
            
            # Determine severity based on type
            severity_map = {
                'grammar': 'error',
                'style': 'warning',
                'clarity': 'info',
                'tone': 'info',
                'vocabulary': 'info'
            }
            
            suggestion = Suggestion(
                id=f"groq_{parsed['type']}_{start_pos}_{hash(parsed['issue'])}",
                document_id=document_id,
                user_id=user_id,
                type=parsed['type'] if parsed['type'] in ['grammar', 'style', 'clarity', 'tone', 'vocabulary'] else 'style',
                text=issue_text,
                suggestion=parsed['suggestion'],
                explanation=parsed['explanation'],
                position=SuggestionPosition(start=start_pos, end=end_pos),
                severity=severity_map.get(parsed['type'], 'info'),
                confidence=90.0,  # High confidence for AI suggestions
                is_applied=False,
                is_dismissed=False,
                created_at=datetime.utcnow()
            )
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Error creating suggestion from parsed data: {e}")
            return None
    
    def analyze_tone(self, content: str) -> ToneAnalysis:
        """Analyze the tone of the text"""
        # Simple tone analysis based on word patterns
        formal_words = ['therefore', 'furthermore', 'consequently', 'moreover', 'nevertheless']
        confident_words = ['will', 'definitely', 'certainly', 'absolutely', 'clearly']
        optimistic_words = ['excellent', 'great', 'wonderful', 'amazing', 'fantastic']
        analytical_words = ['analyze', 'examine', 'evaluate', 'assess', 'consider']
        
        word_count = len(content.split())
        
        formal_score = sum(1 for word in formal_words if word in content.lower()) / max(word_count / 100, 1) * 100
        confident_score = sum(1 for word in confident_words if word in content.lower()) / max(word_count / 100, 1) * 100
        optimistic_score = sum(1 for word in optimistic_words if word in content.lower()) / max(word_count / 100, 1) * 100
        analytical_score = sum(1 for word in analytical_words if word in content.lower()) / max(word_count / 100, 1) * 100
        
        return ToneAnalysis(
            formal=min(formal_score, 100),
            confident=min(confident_score, 100),
            optimistic=min(optimistic_score, 100),
            analytical=min(analytical_score, 100),
            friendly=70.0,  # Default values
            assertive=65.0
        )
    
    def analyze_readability(self, content: str) -> ReadabilityAnalysis:
        """Analyze text readability"""
        if not content.strip():
            return ReadabilityAnalysis(
                flesch_reading_ease=0,
                flesch_kincaid_grade=0,
                automated_readability_index=0,
                coleman_liau_index=0,
                gunning_fog=0,
                smog_index=0,
                overall_score=0
            )
        
        try:
            flesch_ease = textstat.flesch_reading_ease(content)
            flesch_grade = textstat.flesch_kincaid_grade(content)
            ari = textstat.automated_readability_index(content)
            coleman_liau = textstat.coleman_liau_index(content)
            gunning_fog = textstat.gunning_fog(content)
            smog = textstat.smog_index(content)
            
            # Calculate overall score (0-100)
            overall_score = (flesch_ease + (100 - flesch_grade * 10)) / 2
            overall_score = max(0, min(100, overall_score))
            
            return ReadabilityAnalysis(
                flesch_reading_ease=flesch_ease,
                flesch_kincaid_grade=flesch_grade,
                automated_readability_index=ari,
                coleman_liau_index=coleman_liau,
                gunning_fog=gunning_fog,
                smog_index=smog,
                overall_score=overall_score
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
        """Calculate detailed writing statistics"""
        if not content.strip():
            return WritingStats(
                word_count=0,
                sentence_count=0,
                paragraph_count=0,
                avg_sentence_length=0,
                avg_word_length=0,
                passive_voice_percentage=0,
                adverb_percentage=0,
                vocabulary_diversity=0,
                reading_time=0
            )
        
        words = content.split()
        sentences = nltk.sent_tokenize(content)
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len(paragraphs)
        
        avg_sentence_length = word_count / max(sentence_count, 1)
        avg_word_length = sum(len(word) for word in words) / max(word_count, 1)
        
        # Simple passive voice detection
        passive_count = len(re.findall(r'\b(was|were|is|are|been|being)\s+\w+ed\b', content, re.IGNORECASE))
        passive_voice_percentage = (passive_count / max(sentence_count, 1)) * 100
        
        # Adverb detection (words ending in -ly)
        adverb_count = len(re.findall(r'\b\w+ly\b', content, re.IGNORECASE))
        adverb_percentage = (adverb_count / max(word_count, 1)) * 100
        
        # Vocabulary diversity (unique words / total words)
        unique_words = len(set(word.lower() for word in words))
        vocabulary_diversity = (unique_words / max(word_count, 1)) * 100
        
        # Reading time (average 200 words per minute)
        reading_time = max(1, word_count // 200)
        
        return WritingStats(
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            avg_sentence_length=avg_sentence_length,
            avg_word_length=avg_word_length,
            passive_voice_percentage=passive_voice_percentage,
            adverb_percentage=adverb_percentage,
            vocabulary_diversity=vocabulary_diversity,
            reading_time=reading_time
        )
    
    def check_plagiarism(self, content: str) -> float:
        """Simple plagiarism check (returns percentage)"""
        # This is a mock implementation
        # In a real application, you would use a plagiarism detection service
        
        # Check for common phrases that might indicate plagiarism
        common_phrases = [
            "lorem ipsum",
            "the quick brown fox",
            "to be or not to be",
            "it was the best of times"
        ]
        
        plagiarism_score = 0
        for phrase in common_phrases:
            if phrase.lower() in content.lower():
                plagiarism_score += 10
        
        return min(plagiarism_score, 100)

# Global AI service instance
ai_service = AIService()