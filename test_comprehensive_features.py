import requests
import json

def test_comprehensive_features():
    url = "http://localhost:8000/api/ai/suggestions"
    
    # Test content covering all essential features
    test_content = """
    # REAL-TIME GRAMMAR CHECKING
    He go to school every day. She have a car. It do the work. They is happy.
    
    # SPELLING CORRECTION
    I recieve the letter and beleive it was definately from the goverment.
    The accomodation was neccessary for the occassion.
    
    # PUNCTUATION SUGGESTIONS
    The book, that I bought is interesting. "Hello world. She said "goodbye".
    I went to the store and bought apples, oranges, and bananas.
    
    # REPHRASING SUGGESTIONS
    The thing is that we need to utilize the methodology to facilitate the implementation.
    In order to achieve this goal we must consider the aforementioned factors.
    Due to the fact that this is important we should do something about it.
    
    # TONE DETECTION (FORMAL/INFORMAL)
    The paradigm shift facilitated heretofore unprecedented opportunities.
    Notwithstanding the aforementioned considerations, we must proceed.
    Hey dude, this is gonna be awesome! I wanna go there with ya.
    
    # READABILITY ISSUES
    This sentence is extremely long and contains many words that make it difficult to read and understand because it goes on and on without proper breaks which makes it hard to follow the main point that the author is trying to convey to the reader.
    
    # WORD FORM ERRORS
    He runs quick. She speaks good English. The food tastes badly.
    I am very much interested in this topic.
    
    # ARTICLES AND PREPOSITIONS
    I went to a university. She arrived in the airport. We depend in our friends.
    I am interested on music. The weather is good in summer.
    
    # RELATIVE PRONOUNS
    The people which is here are friendly. The thing who broke is expensive.
    The time when I went there was amazing.
    
    # VERB TENSE ERRORS
    I has gone to the store. They have went to the park. She had ate dinner.
    
    # SINGULAR VS PLURAL
    I have many book. She bought a cars. The childrens are playing.
    
    # ESL-SPECIFIC ERRORS
    I have many information. I want learning English. Always I go to school.
    """
    
    payload = {
        "content": test_content,
        "goal": "clarity",
        "tone": "professional", 
        "audience": "general"
    }
    
    try:
        print("🧪 Testing Comprehensive Essential Features...")
        print(f"📝 Content: {test_content.strip()}")
        print("=" * 120)
        
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            
            print(f"✅ Found {len(suggestions)} suggestions:")
            print("=" * 120)
            
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
                print("-" * 80)
                
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
            print("=" * 120)
            print("📊 ESSENTIAL FEATURES COVERAGE:")
            print("-" * 80)
            
            feature_coverage = {
                'spelling': 'Spelling correction',
                'grammar': 'Real-time grammar checking',
                'punctuation': 'Punctuation suggestions',
                'style': 'Rephrasing suggestions',
                'clarity': 'Clarity improvements',
                'tone': 'Tone detection (formal/informal)',
                'esl': 'ESL-specific error handling',
                'fluency': 'Fluency improvements',
                'readability': 'Readability score calculation'
            }
            
            for suggestion_type, type_suggestions in by_type.items():
                coverage = feature_coverage.get(suggestion_type, 'Additional features')
                print(f"   ✅ {suggestion_type}: {len(type_suggestions)} suggestions - {coverage}")
            
            # Check for specific essential features
            print("\n🎯 SPECIFIC ESSENTIAL FEATURES DETECTED:")
            print("-" * 80)
            
            essential_features = {
                'real-time grammar checking': any('grammar' in s.get('type', '').lower() for s in suggestions),
                'spelling correction': any('spelling' in s.get('type', '').lower() for s in suggestions),
                'punctuation suggestions': any('punctuation' in s.get('type', '').lower() for s in suggestions),
                'rephrasing suggestions': any('style' in s.get('type', '').lower() or 'clarity' in s.get('type', '').lower() for s in suggestions),
                'tone detection': any('tone' in s.get('type', '').lower() for s in suggestions),
                'readability calculation': any('readability' in s.get('type', '').lower() for s in suggestions),
                'esl error handling': any('esl' in s.get('type', '').lower() for s in suggestions),
                'word form correction': any('adjective' in s.get('explanation', '').lower() or 'adverb' in s.get('explanation', '').lower() for s in suggestions),
                'article correction': any('article' in s.get('explanation', '').lower() for s in suggestions),
                'preposition correction': any('preposition' in s.get('explanation', '').lower() for s in suggestions),
                'relative pronoun handling': any('relative' in s.get('explanation', '').lower() or 'pronoun' in s.get('explanation', '').lower() for s in suggestions),
                'verb tense correction': any('tense' in s.get('explanation', '').lower() for s in suggestions),
                'singular/plural detection': any('singular' in s.get('explanation', '').lower() or 'plural' in s.get('explanation', '').lower() for s in suggestions)
            }
            
            for feature, detected in essential_features.items():
                status = "✅ DETECTED" if detected else "❌ NOT DETECTED"
                print(f"   {status}: {feature}")
            
            # Performance metrics
            print("\n📈 PERFORMANCE METRICS:")
            print("-" * 80)
            print(f"   Total suggestions: {len(suggestions)}")
            print(f"   High severity: {len([s for s in suggestions if s.get('severity') == 'high'])}")
            print(f"   Medium severity: {len([s for s in suggestions if s.get('severity') == 'medium'])}")
            print(f"   Low severity: {len([s for s in suggestions if s.get('severity') == 'low'])}")
            print(f"   High confidence (>90%): {len([s for s in suggestions if s.get('confidence', 0) > 0.9])}")
            
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
    test_comprehensive_features() 