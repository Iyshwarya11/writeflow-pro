import requests
import json

def test_advanced_grammar_features():
    url = "http://localhost:8000/api/ai/suggestions"
    
    # Test content with ALL advanced grammar features
    test_content = """
    # SUBJECT-VERB AGREEMENT ERRORS
    He go to school every day. She have a car. It do the work. They is happy.
    
    # VERB TENSE ERRORS
    I has gone to the store. They have went to the park. She had ate dinner.
    
    # SINGULAR VS PLURAL NOUNS
    I have many book. She bought a cars. The childrens are playing.
    
    # ARTICLES AND PREPOSITIONS
    I went to a university. She arrived in the airport. We depend in our friends.
    
    # RELATIVE PRONOUNS AND CLAUSES
    The people which is here are friendly. The thing who broke is expensive.
    
    # WORD FORM ERRORS (ADJECTIVE/ADVERB/NOUN)
    He runs quick. She speaks good English. The food tastes badly.
    
    # PUNCTUATION AND SENTENCE BOUNDARIES
    The book, that I bought is interesting. "Hello world. She said "goodbye".
    
    # STYLE AND CLARITY ISSUES
    The thing is that we need to utilize the methodology to facilitate the implementation.
    In order to achieve this goal we must consider the aforementioned factors.
    Due to the fact that this is important we should do something about it.
    
    # TONE AND FORMALITY
    The paradigm shift facilitated heretofore unprecedented opportunities.
    Notwithstanding the aforementioned considerations, we must proceed.
    
    # ESL-SPECIFIC ERRORS
    I am interested on music. I have many information. I want learning English.
    Always I go to school. The weather is good in summer.
    
    # CONTEXTUAL REWRITING NEEDED
    The book is on the table. The book is interesting. The book has many pages.
    
    # READABILITY ISSUES
    This sentence is extremely long and contains many words that make it difficult to read and understand because it goes on and on without proper breaks which makes it hard to follow the main point that the author is trying to convey to the reader.
    
    # SPELLING ERRORS
    I recieve the letter and beleive it was definately from the goverment.
    """
    
    payload = {
        "content": test_content,
        "goal": "clarity",
        "tone": "professional", 
        "audience": "general"
    }
    
    try:
        print("🧪 Testing Advanced Grammar Features...")
        print(f"📝 Content: {test_content.strip()}")
        print("=" * 100)
        
        response = requests.post(url, json=payload, timeout=20)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            
            print(f"✅ Found {len(suggestions)} suggestions:")
            print("=" * 100)
            
            # Group suggestions by type
            by_type = {}
            for suggestion in suggestions:
                suggestion_type = suggestion.get('type', 'unknown')
                if suggestion_type not in by_type:
                    by_type[suggestion_type] = []
                by_type[suggestion_type].append(suggestion)
            
            # Display by type with detailed analysis
            for suggestion_type, type_suggestions in by_type.items():
                print(f"\n🔍 {suggestion_type.upper()} SUGGESTIONS ({len(type_suggestions)}):")
                print("-" * 60)
                
                for i, suggestion in enumerate(type_suggestions, 1):
                    print(f"  {i}. Type: {suggestion.get('type', 'unknown')}")
                    print(f"     Category: {suggestion.get('category', 'unknown')}")
                    print(f"     Original: '{suggestion.get('original_text', '')}'")
                    print(f"     Suggested: '{suggestion.get('suggested_text', '')}'")
                    print(f"     Explanation: {suggestion.get('explanation', '')}")
                    print(f"     Confidence: {suggestion.get('confidence', 0)}")
                    print(f"     Severity: {suggestion.get('severity', 'unknown')}")
                    print()
            
            # Summary with feature coverage
            print("=" * 100)
            print("📊 ADVANCED GRAMMAR FEATURE COVERAGE:")
            print("-" * 60)
            
            feature_coverage = {
                'spelling': 'Spelling correction',
                'grammar': 'Subject-verb agreement, Verb tense, Articles, Prepositions',
                'punctuation': 'Punctuation and sentence boundaries',
                'style': 'Style improvements and word choice',
                'clarity': 'Clarity and readability',
                'tone': 'Tone and formality adjustment',
                'esl': 'ESL-specific error handling',
                'fluency': 'Contextual rewriting and fluency',
                'readability': 'Readability enhancement'
            }
            
            for suggestion_type, type_suggestions in by_type.items():
                coverage = feature_coverage.get(suggestion_type, 'Additional features')
                print(f"   ✅ {suggestion_type}: {len(type_suggestions)} suggestions - {coverage}")
            
            # Check for specific advanced features
            print("\n🎯 SPECIFIC ADVANCED FEATURES DETECTED:")
            print("-" * 60)
            
            advanced_features = {
                'subject-verb agreement': any('agreement' in s.get('explanation', '').lower() for s in suggestions),
                'verb tense correction': any('tense' in s.get('explanation', '').lower() for s in suggestions),
                'singular/plural nouns': any('singular' in s.get('explanation', '').lower() or 'plural' in s.get('explanation', '').lower() for s in suggestions),
                'articles and prepositions': any('article' in s.get('explanation', '').lower() or 'preposition' in s.get('explanation', '').lower() for s in suggestions),
                'relative pronouns': any('relative' in s.get('explanation', '').lower() or 'pronoun' in s.get('explanation', '').lower() for s in suggestions),
                'word forms': any('adjective' in s.get('explanation', '').lower() or 'adverb' in s.get('explanation', '').lower() for s in suggestions),
                'punctuation': any('punctuation' in s.get('type', '').lower() for s in suggestions),
                'esl errors': any('esl' in s.get('type', '').lower() for s in suggestions),
                'tone adjustment': any('tone' in s.get('type', '').lower() for s in suggestions),
                'readability': any('readability' in s.get('type', '').lower() for s in suggestions)
            }
            
            for feature, detected in advanced_features.items():
                status = "✅ DETECTED" if detected else "❌ NOT DETECTED"
                print(f"   {status}: {feature}")
            
            if not suggestions:
                print("⚠️ No suggestions found - this might indicate an issue")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Network error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    test_advanced_grammar_features() 