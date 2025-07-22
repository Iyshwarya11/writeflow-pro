# AI Services for advanced text analysis and processing
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional
from groq import Groq
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os

logger = logging.getLogger(__name__)

class AITextAnalyzer:
    """Advanced AI-powered text analysis service"""
    
    def __init__(self, groq_api_key: str, huggingface_api_key: str):
        self.groq_client = Groq(api_key=groq_api_key) if groq_api_key != "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" else None
        self.hf_api_key = huggingface_api_key
        self.hf_headers = {"Authorization": f"Bearer {huggingface_api_key}"} if huggingface_api_key != "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" else None
    
    async def analyze_sentiment_advanced(self, text: str) -> Dict[str, float]:
        """Advanced sentiment analysis using Hugging Face"""
        if not self.hf_headers:
            return self._fallback_sentiment(text)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest",
                    headers=self.hf_headers,
                    json={"inputs": text[:512]}  # Limit text length
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            scores = {item['label'].lower(): item['score'] for item in result[0]}
                            return scores
        except Exception as e:
            logger.error(f"Error in advanced sentiment analysis: {str(e)}")
        
        return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> Dict[str, float]:
        """Fallback sentiment analysis"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "positive", "happy", "love", "best"]
        negative_words = ["bad", "terrible", "awful", "horrible", "negative", "hate", "worst", "sad", "angry", "disappointed"]
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        neutral_count = len(words) - positive_count - negative_count
        
        total = max(1, len(words))
        return {
            "positive": positive_count / total,
            "negative": negative_count / total,
            "neutral": neutral_count / total
        }
    
    async def analyze_emotion(self, text: str) -> Dict[str, float]:
        """Emotion analysis using Hugging Face"""
        if not self.hf_headers:
            return {"neutral": 1.0}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base",
                    headers=self.hf_headers,
                    json={"inputs": text[:512]}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list) and len(result) > 0:
                            emotions = {item['label'].lower(): item['score'] for item in result[0]}
                            return emotions
        except Exception as e:
            logger.error(f"Error in emotion analysis: {str(e)}")
        
        return {"neutral": 1.0}
    
    async def get_text_embeddings(self, text: str) -> Optional[List[float]]:
        """Get text embeddings for similarity comparison"""
        if not self.hf_headers:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2",
                    headers=self.hf_headers,
                    json={"inputs": text[:512]}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if isinstance(result, list):
                            return result
        except Exception as e:
            logger.error(f"Error getting text embeddings: {str(e)}")
        
        return None
    
    async def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate text summary using AI"""
        if not self.groq_client:
            return self._fallback_summary(text, max_length)
        
        try:
            prompt = f"""
            Please provide a concise summary of the following text in no more than {max_length} words:
            
            Text: "{text}"
            
            Summary:
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, accurate summaries."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.3,
                max_tokens=max_length + 50
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._fallback_summary(text, max_length)
    
    def _fallback_summary(self, text: str, max_length: int) -> str:
        """Fallback summary generation"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "No content to summarize."
        
        # Take first few sentences up to max_length
        summary = ""
        for sentence in sentences:
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip() or sentences[0][:max_length] + "..."
    
    async def check_grammar_advanced(self, text: str) -> List[Dict[str, Any]]:
        """Advanced grammar checking using AI"""
        if not self.groq_client:
            return self._fallback_grammar_check(text)
        
        try:
            prompt = f"""
            Please analyze the following text for grammar, spelling, and style errors. 
            Provide specific corrections in JSON format:
            
            Text: "{text}"
            
            Please respond with a JSON array of errors in this format:
            [
                {{
                    "error_type": "grammar|spelling|style",
                    "original": "incorrect text",
                    "correction": "corrected text",
                    "explanation": "why this is wrong and how to fix it",
                    "position": {{"start": 0, "end": 10}},
                    "severity": "low|medium|high"
                }}
            ]
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert grammar and style checker. Provide specific, actionable corrections."},
                    {"role": "user", "content": prompt}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.2,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            try:
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
        except Exception as e:
            logger.error(f"Error in advanced grammar check: {str(e)}")
        
        return self._fallback_grammar_check(text)
    
    def _fallback_grammar_check(self, text: str) -> List[Dict[str, Any]]:
        """Fallback grammar checking"""
        errors = []
        
        # Comprehensive grammar and spelling patterns
        patterns = [
            # Grammar errors
            (r"\bthere\s+is\s+\w+\s+\w+s\b", "Use 'there are' with plural nouns", "grammar"),
            (r"\b(he|she|it)\s+are\b", "Use 'is' with singular subjects", "grammar"),
            (r"\b(they|we|you)\s+is\b", "Use 'are' with plural subjects", "grammar"),
            (r"\bits\s+\w+ing\b", "Consider 'it's' (it is) instead of 'its' (possessive)", "grammar"),
            (r"\byour\s+\w+ing\b", "Consider 'you're' (you are) instead of 'your' (possessive)", "grammar"),
            (r"\bwould\s+of\b", "Use 'would have' instead of 'would of'", "grammar"),
            (r"\bcould\s+of\b", "Use 'could have' instead of 'could of'", "grammar"),
            (r"\bshould\s+of\b", "Use 'should have' instead of 'should of'", "grammar"),
            
            # Spelling errors
            (r"\bteh\b", "Correct spelling: 'the'", "spelling"),
            (r"\badn\b", "Correct spelling: 'and'", "spelling"),
            (r"\brecieve\b", "Correct spelling: 'receive'", "spelling"),
            (r"\boccured\b", "Correct spelling: 'occurred'", "spelling"),
            (r"\bseperate\b", "Correct spelling: 'separate'", "spelling"),
            (r"\bdefinately\b", "Correct spelling: 'definitely'", "spelling"),
            (r"\bneccessary\b", "Correct spelling: 'necessary'", "spelling"),
            
            # Punctuation errors
            (r"\s+,", "Remove space before comma", "punctuation"),
            (r"\s+\.", "Remove space before period", "punctuation"),
            (r"\b(Mr|Dr|Mrs|Ms)\s+[A-Z]", "Add period after abbreviation", "punctuation"),
            
            # Style improvements
            (r"\b(very|really|quite|extremely)\s+\w+", "Use stronger adjective instead of intensifier", "word_choice"),
            (r"\bin order to\b", "Simply use 'to'", "word_choice"),
            (r"\bdue to the fact that\b", "Use 'because'", "word_choice"),
        ]
        
        for pattern, explanation, error_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Generate appropriate correction
                correction = self._generate_correction(match.group(), error_type)
                
                errors.append({
                    "error_type": error_type,
                    "original": match.group(),
                    "correction": correction,
                    "explanation": explanation,
                    "position": {"start": match.start(), "end": match.end()},
                    "severity": self._get_error_severity(error_type),
                    "rule": self._get_grammar_rule(explanation)
                })
        
        return errors
    
    def _generate_correction(self, original: str, error_type: str) -> str:
        """Generate appropriate correction for the error"""
        original_lower = original.lower()
        
        # Spelling corrections
        spelling_map = {
            "teh": "the", "adn": "and", "recieve": "receive",
            "occured": "occurred", "seperate": "separate", 
            "definately": "definitely", "neccessary": "necessary"
        }
        
        if error_type == "spelling" and original_lower in spelling_map:
            return spelling_map[original_lower]
        
        # Grammar corrections
        if "there is" in original_lower:
            return original.replace("is", "are")
        if "its" in original_lower:
            return original.replace("its", "it's")
        if "your" in original_lower:
            return original.replace("your", "you're")
        if "would of" in original_lower:
            return original.replace("of", "have")
        if "could of" in original_lower:
            return original.replace("of", "have")
        if "should of" in original_lower:
            return original.replace("of", "have")
        
        # Word choice improvements
        if "in order to" in original_lower:
            return original.replace("in order to", "to")
        if "due to the fact that" in original_lower:
            return original.replace("due to the fact that", "because")
        
        return f"[Corrected: {original}]"
    
    def _get_error_severity(self, error_type: str) -> str:
        """Get severity level for error type"""
        severity_map = {
            "spelling": "high",
            "grammar": "high",
            "punctuation": "medium", 
            "word_choice": "low",
            "structure": "medium"
        }
        return severity_map.get(error_type, "medium")
    
    def _get_grammar_rule(self, explanation: str) -> str:
        """Extract grammar rule from explanation"""
        if "subject-verb" in explanation.lower():
            return "Subject-Verb Agreement"
        elif "spelling" in explanation.lower():
            return "Spelling"
        elif "punctuation" in explanation.lower():
            return "Punctuation"
        elif "possessive" in explanation.lower():
            return "Possessive vs Contraction"
        else:
            return "General Grammar"
    
    def calculate_readability_advanced(self, text: str) -> Dict[str, float]:
        """Advanced readability analysis"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        
        if not words or not sentences:
            return {"flesch_reading_ease": 0, "flesch_kincaid_grade": 0, "automated_readability_index": 0}
        
        # Flesch Reading Ease
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables = sum(self._count_syllables(word) for word in words) / len(words)
        flesch_reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables) - 15.59
        
        # Automated Readability Index
        characters = sum(len(word) for word in words)
        avg_chars_per_word = characters / len(words)
        automated_readability_index = (4.71 * avg_chars_per_word) + (0.5 * avg_sentence_length) - 21.43
        
        return {
            "flesch_reading_ease": max(0, min(100, flesch_reading_ease)),
            "flesch_kincaid_grade": max(0, flesch_kincaid_grade),
            "automated_readability_index": max(0, automated_readability_index)
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel
        
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)

class PlagiarismDetector:
    """Advanced plagiarism detection service"""
    
    def __init__(self, ai_analyzer: AITextAnalyzer):
        self.ai_analyzer = ai_analyzer
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    async def check_similarity(self, text1: str, text2: str) -> float:
        """Check similarity between two texts"""
        try:
            # Use AI embeddings if available
            embedding1 = await self.ai_analyzer.get_text_embeddings(text1)
            embedding2 = await self.ai_analyzer.get_text_embeddings(text2)
            
            if embedding1 and embedding2:
                # Calculate cosine similarity
                similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
                return float(similarity) * 100
            
        except Exception as e:
            logger.error(f"Error in AI similarity check: {str(e)}")
        
        # Fallback to TF-IDF similarity
        return self._tfidf_similarity(text1, text2)
    
    def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """Calculate TF-IDF based similarity"""
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity) * 100
        except Exception as e:
            logger.error(f"Error in TF-IDF similarity: {str(e)}")
            return 0.0
    
    def detect_paraphrasing(self, original: str, suspected: str) -> Dict[str, Any]:
        """Detect potential paraphrasing"""
        # Split into sentences
        orig_sentences = re.split(r'[.!?]+', original)
        susp_sentences = re.split(r'[.!?]+', suspected)
        
        orig_sentences = [s.strip() for s in orig_sentences if s.strip()]
        susp_sentences = [s.strip() for s in susp_sentences if s.strip()]
        
        paraphrase_matches = []
        
        for i, orig_sent in enumerate(orig_sentences):
            for j, susp_sent in enumerate(susp_sentences):
                similarity = self._tfidf_similarity(orig_sent, susp_sent)
                if similarity > 30:  # Threshold for potential paraphrasing
                    paraphrase_matches.append({
                        "original_sentence": orig_sent,
                        "suspected_sentence": susp_sent,
                        "similarity": similarity,
                        "type": "paraphrase"
                    })
        
        return {
            "matches": paraphrase_matches,
            "paraphrase_score": len(paraphrase_matches) / max(1, len(orig_sentences)) * 100
        }

# Initialize AI services
ai_analyzer = None
plagiarism_detector = None

def initialize_ai_services():
    """Initialize AI services with API keys"""
    global ai_analyzer, plagiarism_detector
    
    groq_key = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    hf_key = os.getenv("HUGGINGFACE_API_KEY", "your-huggingface-api-key-here")
    
    ai_analyzer = AITextAnalyzer(groq_key, hf_key)
    plagiarism_detector = PlagiarismDetector(ai_analyzer)
    
    logger.info("AI services initialized")

# Initialize on import
initialize_ai_services()