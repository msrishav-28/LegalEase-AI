# LegalEase AI Setup Guide

## Project Structure Created

The following project structure has been successfully created:

```
legalease-ai/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core business logic
│   │   ├── database/          # Database models and connections
│   │   ├── celery_app/        # Background task processing
│   │   ├── config.py          # Configuration management
│   │   └── main.py            # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── pyproject.toml        # Python project configuration
│   └── Dockerfile            # Backend container configuration
├── frontend/                  # Next.js React frontend
│   ├── src/
│   │   ├── app/              # Next.js app directory
│   │   ├── components/       # React components
│   │   ├── lib/              # Utility libraries
│   │   └── types/            # TypeScript type definitions
│   ├── package.json          # Node.js dependencies
│   ├── next.config.js        # Next.js configuration
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   ├── tsconfig.json         # TypeScript configuration
│   └── Dockerfile            # Frontend container configuration
├── database/
│   └── init.sql              # PostgreSQL initialization script
├── nginx/
│   └── nginx.conf            # Reverse proxy configuration
├── scripts/
│   ├── setup.sh/.bat         # Setup scripts for Unix/Windows
│   └── dev.sh/.bat           # Development scripts for Unix/Windows
├── docker-compose.yml        # Main service orchestration
├── docker-compose.dev.yml    # Development overrides
├── .env.example              # Environment variables template
├── .env                      # Environment variables (created)
├── .gitignore               # Git ignore rules
├── Makefile                 # Development commands
└── README.md                # Project documentation
```

## Services Configured

### 1. PostgreSQL Database
- **Image**: pgvector/pgvector:pg15
- **Port**: 5432
- **Features**: pgvector extension for vector storage
- **Database**: legalease_ai
- **User**: legalease_user

### 2. Redis Cache
- **Image**: redis:7-alpine
- **Port**: 6379
- **Purpose**: Session management and caching

### 3. RabbitMQ Message Queue
- **Image**: rabbitmq:3-management-alpine
- **Ports**: 5672 (AMQP), 15672 (Management UI)
- **Purpose**: Background task processing

### 4. Backend API
- **Framework**: FastAPI with Python 3.11+
- **Port**: 8000
- **Features**: Async support, automatic API documentation

### 5. Frontend Application
- **Framework**: Next.js 14 with React 18
- **Port**: 3000
- **Features**: TypeScript, Tailwind CSS, modern React patterns

### 6. Nginx Reverse Proxy
- **Port**: 80 (HTTP), 443 (HTTPS ready)
- **Features**: Load balancing, rate limiting, SSL termination

## Environment Configuration

The following environment variables are configured:

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `RABBITMQ_URL`: RabbitMQ connection string

### Security
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT token signing key

### AI/ML Services
- `OPENAI_API_KEY`: OpenAI API key (needs to be set)
- `PINECONE_API_KEY`: Pinecone vector database key (needs to be set)
- `PINECONE_ENVIRONMENT`: Pinecone environment (needs to be set)

### File Upload
- `MAX_FILE_SIZE_MB`: Maximum file size (100MB)
- `ALLOWED_FILE_TYPES`: Allowed file extensions
- `UPLOAD_DIR`: File upload directory

## Next Steps

1. **Update API Keys**: Edit `.env` file and add your actual API keys:
   ```bash
   OPENAI_API_KEY=your-actual-openai-key
   PINECONE_API_KEY=your-actual-pinecone-key
   PINECONE_ENVIRONMENT=your-pinecone-environment
   ```

2. **Start Services**: Use the Makefile commands:
   ```bash
   make up          # Start all services
   make logs        # View logs
   make down        # Stop services
   ```

3. **Access Applications**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - RabbitMQ Management: http://localhost:15672

4. **Development**: Use development mode for hot reloading:
   ```bash
   # Windows
   scripts\dev.bat
   
   # Unix/Linux/Mac
   scripts/dev.sh
   ```

## Requirements Satisfied

This setup satisfies the following requirements from the specification:

- **Requirement 6.1**: Performance and scalability with Redis caching and connection pooling
- **Requirement 6.2**: Database optimization with PostgreSQL and proper indexing setup
- **Requirement 7.1**: Security with JWT authentication and input validation framework
- **Requirement 8.1**: Deployment with Docker containerization and orchestration

## Development Tools

- **Makefile**: Comprehensive development commands
- **Docker Compose**: Multi-service orchestration
- **Hot Reloading**: Both backend and frontend support live reloading
- **Code Quality**: ESLint, Prettier, Black, isort configured
- **Testing**: Jest, Playwright, pytest frameworks configured

The infrastructure is now ready for implementing the LegalEase AI features according to the design specification.