@echo off
REM LegalEase AI Setup Script for Windows
REM This script sets up the development environment

echo 🚀 Setting up LegalEase AI development environment...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ Created .env file. Please update it with your API keys.
) else (
    echo ✅ .env file already exists.
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist backend\uploads mkdir backend\uploads
if not exist nginx\ssl mkdir nginx\ssl
if not exist logs mkdir logs

REM Build Docker images
echo 🔨 Building Docker images...
docker-compose build

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Update .env file with your API keys:
echo    - OPENAI_API_KEY
echo    - PINECONE_API_KEY
echo    - PINECONE_ENVIRONMENT
echo.
echo 2. Start the services:
echo    make up
echo.
echo 3. Access the application:
echo    - Frontend: http://localhost:3000
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs

pause