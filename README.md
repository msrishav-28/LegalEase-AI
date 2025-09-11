# LegalEase AI

A comprehensive legal document analysis platform that leverages advanced AI and NLP capabilities to help legal professionals and businesses analyze, understand, and manage legal documents with multi-jurisdiction support for Indian and US legal systems.

## Features

- **Multi-Jurisdiction Document Analysis**: Automatic detection and analysis of Indian and US legal documents
- **AI-Powered Document Processing**: Advanced text extraction, OCR, and structure analysis
- **Real-time Collaboration**: Live document annotation and team collaboration
- **Interactive Chat Interface**: Contextual AI assistance for document questions
- **Document Comparison**: Semantic search and clause comparison across documents
- **Cross-Border Legal Analysis**: Comparative analysis between Indian and US legal requirements
- **Secure Document Handling**: Enterprise-grade security and data protection

## Architecture

- **Backend**: Python FastAPI with async support
- **Frontend**: Next.js 14 with React 18 and TypeScript
- **Database**: PostgreSQL 15 with pgvector extension for vector storage
- **Cache**: Redis for session management and caching
- **Message Queue**: RabbitMQ for background task processing
- **AI/ML**: OpenAI GPT-4, LangChain, Pinecone vector database
- **Real-time**: WebSocket connections for live collaboration

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Setup

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd legalease-ai
   make setup
   ```

2. **Configure environment variables:**
   Edit the `.env` file and add your API keys:
   ```bash
   OPENAI_API_KEY=your-openai-api-key
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_ENVIRONMENT=your-pinecone-environment
   ```

3. **Start all services:**
   ```bash
   make up
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672

### Development

#### Backend Development
```bash
# Start backend in development mode
make dev-backend

# Run tests
make test-backend

# Run database migrations
make db-migrate
```

#### Frontend Development
```bash
# Install dependencies
cd frontend && npm install

# Start development server
make dev-frontend

# Run tests
make test-frontend
```

## Project Structure

```
legalease-ai/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/               # Next.js React frontend
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── database/              # Database initialization
├── nginx/                 # Reverse proxy configuration
├── docker-compose.yml     # Service orchestration
├── .env.example          # Environment template
└── Makefile              # Development commands
```

## Available Commands

```bash
make help          # Show all available commands
make setup         # Initial project setup
make up            # Start all services
make down          # Stop all services
make logs          # View service logs
make test          # Run all tests
make clean         # Clean up Docker resources
make db-migrate    # Run database migrations
make health        # Check service health
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Key Endpoints

- `POST /api/documents/upload` - Upload legal documents
- `GET /api/documents/{id}/analyze` - Get document analysis
- `POST /api/jurisdiction/detect` - Detect document jurisdiction
- `POST /api/jurisdiction/compare` - Compare cross-border requirements
- `POST /api/chat/ask` - Interactive document Q&A
- `GET /api/documents/compare` - Compare multiple documents

## Environment Variables

Key environment variables (see `.env.example` for complete list):

- `OPENAI_API_KEY` - OpenAI API key for AI analysis
- `PINECONE_API_KEY` - Pinecone API key for vector storage
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key

## Security

- JWT-based authentication
- Rate limiting on API endpoints
- Input validation and sanitization
- Data encryption at rest and in transit
- Audit logging for compliance

## Testing

```bash
# Run all tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend
```

## Deployment

The application is containerized and ready for deployment with Docker Compose or Kubernetes.

For production deployment:
1. Update environment variables in `.env`
2. Configure SSL certificates in `nginx/ssl/`
3. Update `nginx.conf` for HTTPS
4. Use `docker-compose.prod.yml` for production settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team.