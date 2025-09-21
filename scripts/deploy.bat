@echo off
REM LegalEase AI Deployment Script for Windows
REM This script handles deployment to different environments

setlocal enabledelayedexpansion

REM Default values
set ENVIRONMENT=development
set NAMESPACE=legalease-ai
set HELM_RELEASE=legalease-ai
set BUILD_IMAGES=false
set PUSH_IMAGES=false
set REGISTRY=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :check_prereqs
if "%~1"=="-e" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--environment" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-n" (
    set NAMESPACE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--namespace" (
    set NAMESPACE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-r" (
    set HELM_RELEASE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--release" (
    set HELM_RELEASE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-b" (
    set BUILD_IMAGES=true
    shift
    goto :parse_args
)
if "%~1"=="--build" (
    set BUILD_IMAGES=true
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set PUSH_IMAGES=true
    shift
    goto :parse_args
)
if "%~1"=="--push" (
    set PUSH_IMAGES=true
    shift
    goto :parse_args
)
if "%~1"=="--registry" (
    set REGISTRY=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :usage
if "%~1"=="--help" goto :usage

echo [ERROR] Unknown option: %~1
goto :usage

:usage
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   -e, --environment    Environment to deploy to (development^|staging^|production)
echo   -n, --namespace      Kubernetes namespace (default: legalease-ai)
echo   -r, --release        Helm release name (default: legalease-ai)
echo   -b, --build          Build Docker images
echo   -p, --push           Push Docker images to registry
echo   --registry           Docker registry URL
echo   -h, --help           Show this help message
echo.
echo Examples:
echo   %~nx0 -e development -b
echo   %~nx0 -e production -b -p --registry registry.example.com
goto :eof

:check_prereqs
echo [INFO] Starting deployment for environment: %ENVIRONMENT%

REM Validate environment
if not "%ENVIRONMENT%"=="development" if not "%ENVIRONMENT%"=="staging" if not "%ENVIRONMENT%"=="production" (
    echo [ERROR] Invalid environment: %ENVIRONMENT%
    echo [ERROR] Valid environments: development, staging, production
    exit /b 1
)

echo [INFO] Checking prerequisites...

REM Check if kubectl is installed
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo [ERROR] kubectl is not installed or not in PATH
    exit /b 1
)

REM Check if helm is installed
helm version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] helm is not installed or not in PATH
    exit /b 1
)

REM Check if docker is installed (if building images)
if "%BUILD_IMAGES%"=="true" (
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] docker is not installed or not in PATH
        exit /b 1
    )
)

REM Check kubectl connection
kubectl cluster-info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Cannot connect to Kubernetes cluster
    exit /b 1
)

echo [INFO] Prerequisites check passed

REM Build Docker images if requested
if "%BUILD_IMAGES%"=="true" (
    echo [INFO] Building Docker images...
    
    echo [INFO] Building backend image...
    docker build -t legalease-ai/backend:latest ./backend
    if errorlevel 1 (
        echo [ERROR] Failed to build backend image
        exit /b 1
    )
    
    echo [INFO] Building frontend image...
    docker build -t legalease-ai/frontend:latest ./frontend
    if errorlevel 1 (
        echo [ERROR] Failed to build frontend image
        exit /b 1
    )
    
    echo [INFO] Docker images built successfully
)

REM Push Docker images if requested
if "%PUSH_IMAGES%"=="true" (
    if "%REGISTRY%"=="" (
        echo [ERROR] Registry URL is required when pushing images
        exit /b 1
    )
    
    echo [INFO] Pushing Docker images to registry: %REGISTRY%
    
    REM Tag and push backend image
    docker tag legalease-ai/backend:latest %REGISTRY%/legalease-ai/backend:latest
    docker push %REGISTRY%/legalease-ai/backend:latest
    if errorlevel 1 (
        echo [ERROR] Failed to push backend image
        exit /b 1
    )
    
    REM Tag and push frontend image
    docker tag legalease-ai/frontend:latest %REGISTRY%/legalease-ai/frontend:latest
    docker push %REGISTRY%/legalease-ai/frontend:latest
    if errorlevel 1 (
        echo [ERROR] Failed to push frontend image
        exit /b 1
    )
    
    echo [INFO] Docker images pushed successfully
)

REM Create namespace if it doesn't exist
echo [INFO] Creating namespace if it doesn't exist...
kubectl create namespace %NAMESPACE% --dry-run=client -o yaml | kubectl apply -f -

REM Deploy using Helm
echo [INFO] Deploying with Helm...

REM Set values file based on environment
set VALUES_FILE=helm\legalease-ai\values-%ENVIRONMENT%.yaml
if not exist "%VALUES_FILE%" (
    echo [WARNING] Environment-specific values file not found: %VALUES_FILE%
    echo [WARNING] Using default values.yaml
    set VALUES_FILE=helm\legalease-ai\values.yaml
)

REM Build Helm command
set HELM_CMD=helm upgrade --install --namespace %NAMESPACE% --values %VALUES_FILE% --wait --timeout 10m

REM Add registry override if specified
if not "%REGISTRY%"=="" (
    set HELM_CMD=%HELM_CMD% --set global.imageRegistry=%REGISTRY%
)

REM Execute helm command
%HELM_CMD% %HELM_RELEASE% helm\legalease-ai\
if errorlevel 1 (
    echo [ERROR] Helm deployment failed
    exit /b 1
)

echo [INFO] Deployment completed successfully!

REM Show deployment status
echo [INFO] Checking deployment status...
kubectl get pods -n %NAMESPACE%
kubectl get services -n %NAMESPACE%
kubectl get ingress -n %NAMESPACE%

echo [INFO] Deployment script completed!