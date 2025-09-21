#!/bin/bash

echo "🚀 Deploying LegalEase AI to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Logging into Railway..."
railway login

# Create new project or link existing
echo "📦 Setting up Railway project..."
railway init

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add --database postgresql

# Add Redis database
echo "🔴 Adding Redis database..."
railway add --database redis

# Set environment variables
echo "⚙️ Setting up environment variables..."
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set SECRET_KEY=$(openssl rand -base64 32)
railway variables set JWT_SECRET_KEY=$(openssl rand -base64 32)
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set MAX_FILE_SIZE=10485760
railway variables set UPLOAD_DIR=/app/uploads
railway variables set LOG_LEVEL=INFO

# Deploy the application
echo "🚀 Deploying application..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your application will be available at the Railway-provided URL"
echo "📊 Check the Railway dashboard for logs and monitoring"