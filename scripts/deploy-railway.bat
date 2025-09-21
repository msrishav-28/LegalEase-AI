@echo off
echo 🚀 Deploying LegalEase AI to Railway...

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Login to Railway
echo 🔐 Logging into Railway...
railway login

REM Create new project or link existing
echo 📦 Setting up Railway project...
railway init

REM Add PostgreSQL database
echo 🗄️ Adding PostgreSQL database...
railway add --database postgresql

REM Add Redis database
echo 🔴 Adding Redis database...
railway add --database redis

REM Set environment variables
echo ⚙️ Setting up environment variables...
railway variables set ENVIRONMENT=production
railway variables set DEBUG=false
railway variables set ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set MAX_FILE_SIZE=10485760
railway variables set UPLOAD_DIR=/app/uploads
railway variables set LOG_LEVEL=INFO

REM Deploy the application
echo 🚀 Deploying application...
railway up

echo ✅ Deployment complete!
echo 🌐 Your application will be available at the Railway-provided URL
echo 📊 Check the Railway dashboard for logs and monitoring
pause