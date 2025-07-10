# WriteFlow Pro - AI-Powered Writing Assistant

A comprehensive document editor with AI-powered writing assistance, real-time collaboration, and advanced analytics.

## Features

### 🤖 AI-Powered Writing Assistance
- **Grammar & Style Checking**: Real-time grammar corrections and style improvements
- **Tone Analysis**: Analyze and adjust writing tone for different audiences
- **Readability Scoring**: Get readability metrics and suggestions for improvement
- **Vocabulary Enhancement**: AI-powered vocabulary suggestions and improvements
- **Plagiarism Detection**: Basic plagiarism checking capabilities

### 📝 Advanced Document Management
- **Rich Text Editor**: Full-featured editor with formatting tools
- **Auto-Save**: Automatic document saving with version control
- **Document Organization**: Tags, folders, and search functionality
- **Collaboration**: Real-time document sharing and collaboration
- **Export Options**: Multiple export formats (PDF, Word, etc.)

### 📊 Writing Analytics
- **Writing Statistics**: Word count, reading time, grade level analysis
- **Progress Tracking**: Writing goals and productivity metrics
- **Performance Insights**: Detailed analytics on writing patterns
- **Improvement Suggestions**: Personalized recommendations for better writing

### 🎨 Modern User Experience
- **Dark/Light Mode**: Customizable theme preferences
- **Focus Mode**: Distraction-free writing environment
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Keyboard Shortcuts**: Efficient workflow with keyboard shortcuts
- **Voice Input**: Speech-to-text functionality

## Tech Stack

### Frontend
- **Next.js 13+** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern UI component library
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database with Motor async driver
- **JWT Authentication** - Secure user authentication
- **Groq API** - AI-powered language processing
- **NLTK & TextStat** - Text analysis and processing

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- MongoDB (local or cloud)
- Groq API key (optional, for enhanced AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd writeflow-pro
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   npm run install:backend
   ```

4. **Set up environment variables**
   
   Frontend (.env.local):
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   ```
   
   Backend (backend/.env):
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=writeflow_pro
   SECRET_KEY=your-secret-key-change-this-in-production
   GROQ_API_KEY=your-groq-api-key-here
   ```

5. **Start the development servers**
   ```bash
   # Start both frontend and backend
   npm run dev:full
   
   # Or start them separately
   npm run dev          # Frontend only
   npm run backend      # Backend only
   ```

6. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development

### Project Structure
```
writeflow-pro/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   ├── page.tsx          # Main application
│   └── not-found.tsx     # 404 page
├── components/            # React components
│   └── ui/               # shadcn/ui components
├── lib/                  # Utility libraries
│   ├── api.ts           # API client
│   └── utils.ts         # Helper functions
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── models/      # Pydantic models
│   │   ├── routers/     # API routes
│   │   ├── services/    # Business logic
│   │   └── main.py      # FastAPI app
│   ├── requirements.txt # Python dependencies
│   └── run.py          # Server runner
└── README.md
```

### API Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

#### Documents
- `GET /api/documents/` - List documents
- `POST /api/documents/` - Create document
- `GET /api/documents/{id}` - Get document
- `PUT /api/documents/{id}` - Update document
- `DELETE /api/documents/{id}` - Delete document

#### AI Features
- `POST /api/ai/suggestions` - Generate AI suggestions
- `POST /api/ai/tone-analysis` - Analyze text tone
- `POST /api/ai/plagiarism-check` - Check plagiarism
- `GET /api/analytics/document/{id}` - Document analytics

### Environment Variables

#### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

#### Backend
- `MONGODB_URL` - MongoDB connection string
- `DATABASE_NAME` - Database name
- `SECRET_KEY` - JWT secret key
- `GROQ_API_KEY` - Groq API key for enhanced AI features
- `CORS_ORIGINS` - Allowed CORS origins

## Deployment

### Frontend (Vercel/Netlify)
1. Build the project: `npm run build`
2. Deploy the `out` directory (static export)
3. Set environment variables in deployment platform

### Backend (Railway/Heroku/DigitalOcean)
1. Set up MongoDB database
2. Configure environment variables
3. Deploy using Docker or direct Python deployment

### Docker Deployment
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["python", "run.py"]
```

## Features in Detail

### AI Writing Assistant
- **Real-time Suggestions**: Get grammar, style, and clarity suggestions as you type
- **Context-Aware**: Suggestions adapt to your writing goal (professional, academic, creative, etc.)
- **Multiple Languages**: Support for multiple languages and locales
- **Confidence Scoring**: Each suggestion includes a confidence score

### Document Management
- **Version Control**: Track document versions and changes
- **Collaboration**: Share documents with team members
- **Organization**: Use tags and folders to organize documents
- **Search**: Full-text search across all documents

### Analytics Dashboard
- **Writing Metrics**: Track words written, time spent, and productivity
- **Readability Analysis**: Flesch-Kincaid, SMOG, and other readability scores
- **Tone Analysis**: Understand the emotional tone of your writing
- **Progress Tracking**: Set and track writing goals

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@writeflowpro.com or join our Discord community.

## Roadmap

- [ ] Real-time collaborative editing
- [ ] Advanced plagiarism detection
- [ ] Integration with Google Docs/Word
- [ ] Mobile app development
- [ ] Advanced AI models integration
- [ ] Team workspace features
- [ ] Advanced export options
- [ ] Plugin system for extensions