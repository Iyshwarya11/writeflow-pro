import requests
import json

def test_api():
    url = "http://localhost:8000/api/ai/suggestions"
    
    # Test content with multiple errors
    test_content = """
    This is a test sentence with recieve and definately and beleive. 
    I went to schol yesterday and it was very good. 
    The goverment should do something about this problem.
    I beleive that we need to make a change.
    """
    
    payload = {
        "content": test_content,
        "goal": "clarity",
        "tone": "professional", 
        "audience": "general"
    }
    
    try:
        print("🧪 Testing API with content containing multiple errors...")
        print(f"📝 Content: {test_content.strip()}")
        
        response = requests.post(url, json=payload, timeout=10)
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('suggestions', [])
            
            print(f"✅ Found {len(suggestions)} suggestions:")
            print()
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"🔍 Suggestion {i}:")
                print(f"   Type: {suggestion.get('type', 'unknown')}")
                print(f"   Original: '{suggestion.get('original_text', '')}'")
                print(f"   Suggested: '{suggestion.get('suggested_text', '')}'")
                print(f"   Explanation: {suggestion.get('explanation', '')}")
                print(f"   Confidence: {suggestion.get('confidence', 0)}")
                print(f"   Severity: {suggestion.get('severity', 'unknown')}")
                print()
            
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
    test_api() 