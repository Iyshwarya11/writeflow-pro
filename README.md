# WriteFlow Pro Backend

A FastAPI backend for WriteFlow Pro document editor with AI-powered writing assistance using LangChain, Ollama Llama3, and SQLite database.

## Features

- **AI-Powered Writing Assistance**: Grammar checking, style suggestions, tone analysis using Llama3
- **Document Management**: CRUD operations with version control
- **Real-time Analytics**: Readability scores, writing statistics, keyword extraction
- **User Authentication**: JWT-based authentication with SQLite
- **Collaborative Editing**: Document sharing and collaboration features
- **Plagiarism Detection**: Basic plagiarism checking capabilities
- **Vocabulary Enhancement**: AI-powered vocabulary improvement suggestions

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **Ollama**: Local LLM runtime for Llama3
- **SQLite**: Lightweight, file-based database
- **Pydantic**: Data validation using Python type annotations
- **SQLAlchemy**: SQL toolkit and ORM
- **JWT**: JSON Web Tokens for authentication

## Setup

### Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running locally
3. **Llama3 model** pulled in Ollama

### Installation

1. **Clone and navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   DATABASE_URL=sqlite:///./writeflow.db
   OLLAMA_BASE_URL=http://localhost:11434
   SECRET_KEY=your_secret_key_here
   ```

5. **Set up Ollama and Llama3**:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Llama3 model
   ollama pull llama3
   
   # Start Ollama service
   ollama serve
   ```

6. **Download NLTK data**:
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

### Running the Server

1. **Development mode**:
   ```bash
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Production mode**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`
- **OpenAPI schema**: `http://localhost:8000/openapi.json`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile
- `POST /api/auth/logout` - User logout

### Documents
- `GET /api/documents/` - List user documents
- `POST /api/documents/` - Create new document
- `GET /api/documents/{id}` - Get document by ID
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/documents/{id}/duplicate` - Duplicate document

### AI Suggestions
- `POST /api/ai/suggestions` - Generate AI suggestions
- `GET /api/ai/suggestions/{document_id}` - Get document suggestions
- `PUT /api/ai/suggestions/{id}/apply` - Apply suggestion
- `PUT /api/ai/suggestions/{id}/dismiss` - Dismiss suggestion
- `POST /api/ai/tone-analysis` - Analyze text tone
- `POST /api/ai/plagiarism-check` - Check for plagiarism
- `POST /api/ai/vocabulary-enhancement` - Enhance vocabulary

### Analytics
- `GET /api/analytics/document/{id}` - Get document analytics
- `GET /api/analytics/document/{id}/readability` - Get readability analysis
- `GET /api/analytics/document/{id}/keywords` - Extract keywords
- `GET /api/analytics/user/stats` - Get user writing statistics
- `POST /api/analytics/document/{id}/compare` - Compare document versions

## Database Schema

The SQLite database includes the following tables:

### Users Table
- `id` (String, Primary Key)
- `email` (String, Unique)
- `full_name` (String)
- `hashed_password` (String)
- `created_at`, `updated_at` (DateTime)
- `is_active` (Boolean)
- `subscription_tier` (String)
- `preferences` (JSON)

### Documents Table
- `id` (String, Primary Key)
- `title` (String)
- `content` (Text)
- `user_id` (String)
- `created_at`, `updated_at` (DateTime)
- `word_count`, `reading_time` (Integer)
- `tags` (JSON)
- `language`, `writing_goal`, `status` (String)
- `is_public` (Boolean)
- `version` (Integer)
- `collaborators` (JSON)

### Suggestions Table
- `id` (String, Primary Key)
- `document_id` (String)
- `type`, `text`, `suggestion`, `explanation` (String)
- `position` (JSON)
- `severity` (String)
- `confidence` (Float)
- `created_at` (DateTime)
- `is_applied`, `is_dismissed` (Boolean)

## Configuration

### Environment Variables

- `DATABASE_URL`: SQLite database file path (default: sqlite:///./writeflow.db)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

### Ollama Configuration

The service automatically:
1. Connects to Ollama at startup
2. Checks if Llama3 model is available
3. Pulls the model if not present
4. Initializes the LangChain integration

## Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   └── services/            # Business logic services
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── run.py                  # Server runner
└── README.md
```

### Adding New Features

1. **Create Pydantic models** in `app/models/`
2. **Add database models** in `app/database.py`
3. **Implement business logic** in `app/services/`
4. **Create API routes** in `app/routers/`
5. **Update main.py** to include new routers

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

### Environment Setup

Ensure all environment variables are properly set in production:
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Set up SSL/TLS termination
- Configure logging levels

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**:
   - Ensure Ollama is running: `ollama serve`
   - Check if Llama3 model is available: `ollama list`
   - Verify OLLAMA_BASE_URL in environment

2. **Database Issues**:
   - Check if SQLite file is writable
   - Ensure database directory exists
   - Verify DATABASE_URL format

3. **NLTK Data Missing**:
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

4. **Permission Errors**:
   - Check file permissions for database
   - Verify user has write access to directory
   - Ensure JWT token is valid

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.