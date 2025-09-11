#!/bin/bash

# Development script for LegalEase AI
# Starts services in development mode with hot reloading

set -e

echo "🔥 Starting LegalEase AI in development mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run 'make setup' first."
    exit 1
fi

# Start services with development configuration
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

echo "🎉 Development environment started!"