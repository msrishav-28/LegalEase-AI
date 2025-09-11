#!/bin/bash

# LegalEase AI Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up LegalEase AI development environment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please update it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p nginx/ssl
mkdir -p logs

# Set permissions
chmod +x scripts/*.sh

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - PINECONE_API_KEY"
echo "   - PINECONE_ENVIRONMENT"
echo ""
echo "2. Start the services:"
echo "   make up"
echo ""
echo "3. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"