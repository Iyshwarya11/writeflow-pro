# Grammarly Clone - Advanced Writing Assistant

A comprehensive writing assistant built with Next.js, FastAPI, and modern AI technologies. This application provides real-time grammar checking, writing suggestions, plagiarism detection, and writing analytics.

## Features

### Frontend (Next.js + Tailwind + shadcn/ui)
- **Real-time Editor**: Advanced text editor with live grammar checking
- **Smart Suggestions**: AI-powered writing suggestions with explanations
- **Writing Analytics**: Comprehensive insights and performance tracking
- **Plagiarism Checker**: Content originality verification
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Modern UI**: Clean, professional interface with smooth animations

### Backend (FastAPI + MongoDB)
- **AI-Powered Suggestions**: Using Groq API and Hugging Face models
- **Grammar Checking**: Advanced grammar and style analysis
- **Plagiarism Detection**: Multi-source plagiarism checking
- **Document Management**: Full CRUD operations for documents
- **User Analytics**: Writing statistics and trends
- **RESTful API**: Well-documented API endpoints

## Tech Stack

### Frontend
- **Next.js 13**: React framework with App Router
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Modern component library
- **Lucide React**: Beautiful icons
- **TypeScript**: Type-safe development

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for document storage
- **Groq API**: Fast AI inference
- **Hugging Face**: Pre-trained AI models
- **Motor**: Async MongoDB driver

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- MongoDB
- Groq API key
- Hugging Face API key (optional)

### Frontend Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to API directory
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and MongoDB URI

# Start the server
python main.py
```

### Database Setup
```bash
# Start MongoDB (if running locally)
mongod

# The application will automatically create indexes and collections
```

## Environment Variables

Create a `.env` file in the `api` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
MONGODB_URI=mongodb://localhost:27017/grammarly_clone
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
CORS_ORIGINS=http://localhost:3000
DEBUG=True
```

## API Endpoints

### Documents
- `POST /api/documents` - Create document
- `GET /api/documents/{id}` - Get document
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document
- `GET /api/users/{user_id}/documents` - Get user documents

### Suggestions
- `POST /api/suggestions` - Get writing suggestions
- `GET /api/suggestions/{document_id}` - Get cached suggestions

### Plagiarism
- `POST /api/plagiarism/check` - Check for plagiarism
- `GET /api/plagiarism/{document_id}` - Get plagiarism results

### Analytics
- `GET /api/users/{user_id}/statistics` - Get writing statistics
- `GET /api/users/{user_id}/trends` - Get writing trends

## Features in Detail

### Real-time Grammar Checking
- Uses Hugging Face CoLA model for grammar validation
- Highlights errors with explanations
- Provides suggestions for improvements

### AI-Powered Suggestions
- Groq API integration for intelligent suggestions
- Context-aware improvements
- Writing goal optimization (clarity, engagement, tone)

### Plagiarism Detection
- Multi-source checking (web, academic, publications)
- Similarity scoring
- Source attribution and links

### Writing Analytics
- Word count and reading time
- Writing quality scores
- Progress tracking
- Performance insights

## Development

### Frontend Development
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Backend Development
```bash
# Start with auto-reload
python main.py

# Run tests (if implemented)
pytest

# Format code
black .
```

## Deployment

### Frontend (Vercel/Netlify)
```bash
# Build the project
npm run build

# Deploy to Vercel
vercel deploy

# Or deploy to Netlify
netlify deploy --prod
```

### Backend (Railway/Heroku)
```bash
# Create Dockerfile for containerization
# Push to your preferred cloud platform
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Groq for fast AI inference
- Hugging Face for pre-trained models
- shadcn/ui for beautiful components
- The open-source community for amazing tools

## Support

For support, email support@example.com or join our Discord community.