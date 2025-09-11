@echo off
REM Development script for LegalEase AI
REM Starts services in development mode with hot reloading

echo 🔥 Starting LegalEase AI in development mode...

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found. Run setup.bat first.
    pause
    exit /b 1
)

REM Start services with development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo 🎉 Development environment started!