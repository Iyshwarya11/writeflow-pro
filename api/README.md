# Grammarly Clone API

This is the backend API for the Grammarly clone, providing AI-powered writing suggestions, plagiarism detection, and analytics.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. API Keys Setup (Optional but Recommended)

For the best AI suggestions, you can set up API keys for Groq or Hugging Face:

#### Option A: Groq API (Recommended - Fast and Free)
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up and get your API key
3. Set environment variable:
```bash
export GROQ_API_KEY="your-groq-api-key-here"
```

#### Option B: Hugging Face API
1. Go to [Hugging Face](https://huggingface.co/settings/tokens)
2. Create an account and get your API token
3. Set environment variable:
```bash
export HUGGINGFACE_API_KEY="your-huggingface-api-key-here"
```

### 3. Run the API
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Features

- **AI Writing Suggestions**: Grammar, clarity, tone, and style improvements
- **Plagiarism Detection**: Check content against web and academic sources
- **Writing Analytics**: Readability, sentiment, and engagement analysis
- **Document Management**: Create, update, and manage documents
- **User Insights**: Writing performance tracking and recommendations

## API Endpoints

- `POST /api/ai/suggestions` - Get AI writing suggestions
- `POST /api/ai/plagiarism/check` - Check for plagiarism
- `POST /api/ai/insights` - Get writing insights
- `GET /api/documents` - List documents
- `POST /api/documents` - Create document
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

## How it Works

1. **Primary**: Uses Groq API for fast, high-quality suggestions
2. **Fallback**: Uses Hugging Face API if Groq is unavailable
3. **Final Fallback**: Uses built-in grammar and style rules

The system automatically falls back to the next option if the previous one fails, ensuring you always get suggestions.

## Frontend Integration

The frontend runs on `http://localhost:3000` and automatically connects to this API on `http://localhost:8000`.

## Notes

- If no API keys are provided, the system will use the built-in fallback suggestions
- The fallback suggestions are comprehensive and include grammar, spelling, and style improvements
- All suggestions are returned in a consistent format for the frontend 