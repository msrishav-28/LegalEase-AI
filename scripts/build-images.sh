#!/bin/bash

# LegalEase AI Docker Image Build Script
# This script builds all Docker images for the application

set -e

# Default values
REGISTRY=""
TAG="latest"
PUSH=false
PLATFORM="linux/amd64"

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
    echo "  -r, --registry       Docker registry URL"
    echo "  -t, --tag            Image tag (default: latest)"
    echo "  -p, --push           Push images to registry after building"
    echo "  --platform           Target platform (default: linux/amd64)"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -t v1.0.0"
    echo "  $0 -r registry.example.com -t v1.0.0 -p"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        --platform)
            PLATFORM="$2"
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

print_status "Building LegalEase AI Docker images..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    print_error "docker is not installed or not in PATH"
    exit 1
fi

# Set image names
if [[ -n "$REGISTRY" ]]; then
    BACKEND_IMAGE="$REGISTRY/legalease-ai/backend:$TAG"
    FRONTEND_IMAGE="$REGISTRY/legalease-ai/frontend:$TAG"
else
    BACKEND_IMAGE="legalease-ai/backend:$TAG"
    FRONTEND_IMAGE="legalease-ai/frontend:$TAG"
fi

# Build backend image
print_status "Building backend image: $BACKEND_IMAGE"
docker build \
    --platform "$PLATFORM" \
    -t "$BACKEND_IMAGE" \
    -f backend/Dockerfile \
    backend/

if [[ $? -ne 0 ]]; then
    print_error "Failed to build backend image"
    exit 1
fi

# Build frontend image
print_status "Building frontend image: $FRONTEND_IMAGE"
docker build \
    --platform "$PLATFORM" \
    -t "$FRONTEND_IMAGE" \
    -f frontend/Dockerfile \
    frontend/

if [[ $? -ne 0 ]]; then
    print_error "Failed to build frontend image"
    exit 1
fi

print_status "All images built successfully!"

# Push images if requested
if [[ "$PUSH" == true ]]; then
    if [[ -z "$REGISTRY" ]]; then
        print_error "Registry URL is required when pushing images"
        exit 1
    fi
    
    print_status "Pushing images to registry..."
    
    print_status "Pushing backend image..."
    docker push "$BACKEND_IMAGE"
    
    if [[ $? -ne 0 ]]; then
        print_error "Failed to push backend image"
        exit 1
    fi
    
    print_status "Pushing frontend image..."
    docker push "$FRONTEND_IMAGE"
    
    if [[ $? -ne 0 ]]; then
        print_error "Failed to push frontend image"
        exit 1
    fi
    
    print_status "All images pushed successfully!"
fi

# Show image information
print_status "Built images:"
docker images | grep -E "(legalease-ai|$REGISTRY.*legalease-ai)" | head -10

print_status "Build script completed!"