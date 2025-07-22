import requests
import json

def test_comprehensive_suggestions():
    url = "http://localhost:8000/api/ai/suggestions"
    
    # Test content with multiple types of errors
    test_content = """
    I recieve the letter and beleive it was definately from the goverment. 
    Its very good and I think its going to be really helpful for us.
    The thing is that we need to utilize the methodology to facilitate the implementation of the paradigm.
    In order to achieve this goal, we must consider the aforementioned factors.
    Due to the fact that this is important, we should do something about it.
    At this point in time, we are gonna have to make a decision.
    The stuff that we discussed was kinda interesting but sort of confusing.
    I went to schol yesterday and it was very good.
    This sentence is extremely long and contains many words that make it difficult to read and understand because it goes on and on without proper breaks which makes it hard to follow the main point that the author is trying to convey.
    Although we tried our best.
    Because of the weather.
    """
    
    payload = {
        "content": test_content,
        "goal": "clarity",
        "tone": "professional", 
        "audience": "general"
    }
    
    try:
        print("🧪 Testing Comprehensive Suggestions...")
        print(f"📝 Content: {test_content.strip()}")
        print("=" * 80)
        
        response = requests.post(url, json=payload, timeout=15)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            
            print(f"✅ Found {len(suggestions)} suggestions:")
            print("=" * 80)
            
            # Group suggestions by type
            by_type = {}
            for suggestion in suggestions:
                suggestion_type = suggestion.get('type', 'unknown')
                if suggestion_type not in by_type:
                    by_type[suggestion_type] = []
                by_type[suggestion_type].append(suggestion)
            
            # Display by type
            for suggestion_type, type_suggestions in by_type.items():
                print(f"\n🔍 {suggestion_type.upper()} SUGGESTIONS ({len(type_suggestions)}):")
                print("-" * 50)
                
                for i, suggestion in enumerate(type_suggestions, 1):
                    print(f"  {i}. Type: {suggestion.get('type', 'unknown')}")
                    print(f"     Original: '{suggestion.get('original_text', '')}'")
                    print(f"     Suggested: '{suggestion.get('suggested_text', '')}'")
                    print(f"     Explanation: {suggestion.get('explanation', '')}")
                    print(f"     Confidence: {suggestion.get('confidence', 0)}")
                    print(f"     Severity: {suggestion.get('severity', 'unknown')}")
                    print()
            
            # Summary
            print("=" * 80)
            print("📊 SUMMARY:")
            for suggestion_type, type_suggestions in by_type.items():
                print(f"   {suggestion_type}: {len(type_suggestions)} suggestions")
            
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
    test_comprehensive_suggestions() 