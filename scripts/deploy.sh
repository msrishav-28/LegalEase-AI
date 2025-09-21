#!/bin/bash

# LegalEase AI Deployment Script
# This script handles deployment to different environments

set -e

# Default values
ENVIRONMENT="development"
NAMESPACE="legalease-ai"
HELM_RELEASE="legalease-ai"
BUILD_IMAGES=false
PUSH_IMAGES=false
REGISTRY=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment    Environment to deploy to (development|staging|production)"
    echo "  -n, --namespace      Kubernetes namespace (default: legalease-ai)"
    echo "  -r, --release        Helm release name (default: legalease-ai)"
    echo "  -b, --build          Build Docker images"
    echo "  -p, --push           Push Docker images to registry"
    echo "  --registry           Docker registry URL"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e development -b"
    echo "  $0 -e production -b -p --registry registry.example.com"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -r|--release)
            HELM_RELEASE="$2"
            shift 2
            ;;
        -b|--build)
            BUILD_IMAGES=true
            shift
            ;;
        -p|--push)
            PUSH_IMAGES=true
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Valid environments: development, staging, production"
    exit 1
fi

print_status "Starting deployment for environment: $ENVIRONMENT"

# Check prerequisites
print_status "Checking prerequisites..."

# Check if kubectl is installed and configured
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed or not in PATH"
    exit 1
fi

# Check if docker is installed (if building images)
if [[ "$BUILD_IMAGES" == true ]] && ! command -v docker &> /dev/null; then
    print_error "docker is not installed or not in PATH"
    exit 1
fi

# Check kubectl connection
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_status "Prerequisites check passed"

# Build Docker images if requested
if [[ "$BUILD_IMAGES" == true ]]; then
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t legalease-ai/backend:latest ./backend
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t legalease-ai/frontend:latest ./frontend
    
    print_status "Docker images built successfully"
fi

# Push Docker images if requested
if [[ "$PUSH_IMAGES" == true ]]; then
    if [[ -z "$REGISTRY" ]]; then
        print_error "Registry URL is required when pushing images"
        exit 1
    fi
    
    print_status "Pushing Docker images to registry: $REGISTRY"
    
    # Tag and push backend image
    docker tag legalease-ai/backend:latest $REGISTRY/legalease-ai/backend:latest
    docker push $REGISTRY/legalease-ai/backend:latest
    
    # Tag and push frontend image
    docker tag legalease-ai/frontend:latest $REGISTRY/legalease-ai/frontend:latest
    docker push $REGISTRY/legalease-ai/frontend:latest
    
    print_status "Docker images pushed successfully"
fi

# Create namespace if it doesn't exist
print_status "Creating namespace if it doesn't exist..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Deploy using Helm
print_status "Deploying with Helm..."

# Set values file based on environment
VALUES_FILE="helm/legalease-ai/values-${ENVIRONMENT}.yaml"
if [[ ! -f "$VALUES_FILE" ]]; then
    print_warning "Environment-specific values file not found: $VALUES_FILE"
    print_warning "Using default values.yaml"
    VALUES_FILE="helm/legalease-ai/values.yaml"
fi

# Helm upgrade/install command
HELM_ARGS=(
    upgrade
    --install
    --namespace "$NAMESPACE"
    --values "$VALUES_FILE"
    --wait
    --timeout 10m
)

# Add registry override if specified
if [[ -n "$REGISTRY" ]]; then
    HELM_ARGS+=(--set "global.imageRegistry=$REGISTRY")
fi

# Execute helm command
helm "${HELM_ARGS[@]}" "$HELM_RELEASE" helm/legalease-ai/

print_status "Deployment completed successfully!"

# Show deployment status
print_status "Checking deployment status..."
kubectl get pods -n "$NAMESPACE"
kubectl get services -n "$NAMESPACE"
kubectl get ingress -n "$NAMESPACE"

print_status "Deployment script completed!"