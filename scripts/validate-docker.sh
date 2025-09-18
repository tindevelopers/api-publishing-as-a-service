#!/bin/bash

# Docker validation script for AI Content Publisher API
# This script validates the Docker setup and configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Docker Validation Script for AI Content Publisher API${NC}"
echo "=================================================="

# Check if Docker is installed
echo -e "${YELLOW}📋 Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed${NC}"

# Check if Docker is running
echo -e "${YELLOW}📋 Checking Docker daemon...${NC}"
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running. Please start Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon is running${NC}"

# Check if Docker Compose is available
echo -e "${YELLOW}📋 Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is available${NC}"

# Check required files
echo -e "${YELLOW}📋 Checking required files...${NC}"
required_files=(
    "Dockerfile"
    "Dockerfile.prod"
    "docker-compose.yml"
    "docker-compose.prod.yml"
    "requirements.txt"
    "requirements-prod.txt"
    ".dockerignore"
    ".env.example"
    "env.prod.example"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Required file missing: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Found: $file${NC}"
done

# Validate Dockerfile syntax
echo -e "${YELLOW}📋 Validating Dockerfile syntax...${NC}"
if docker build --dry-run -f Dockerfile . &> /dev/null; then
    echo -e "${GREEN}✅ Dockerfile syntax is valid${NC}"
else
    echo -e "${RED}❌ Dockerfile syntax is invalid${NC}"
    exit 1
fi

# Validate production Dockerfile syntax
echo -e "${YELLOW}📋 Validating production Dockerfile syntax...${NC}"
if docker build --dry-run -f Dockerfile.prod . &> /dev/null; then
    echo -e "${GREEN}✅ Production Dockerfile syntax is valid${NC}"
else
    echo -e "${RED}❌ Production Dockerfile syntax is invalid${NC}"
    exit 1
fi

# Validate docker-compose syntax
echo -e "${YELLOW}📋 Validating docker-compose syntax...${NC}"
if docker-compose config &> /dev/null; then
    echo -e "${GREEN}✅ docker-compose.yml syntax is valid${NC}"
else
    echo -e "${RED}❌ docker-compose.yml syntax is invalid${NC}"
    exit 1
fi

# Validate production docker-compose syntax
echo -e "${YELLOW}📋 Validating production docker-compose syntax...${NC}"
if docker-compose -f docker-compose.prod.yml config &> /dev/null; then
    echo -e "${GREEN}✅ docker-compose.prod.yml syntax is valid${NC}"
else
    echo -e "${RED}❌ docker-compose.prod.yml syntax is invalid${NC}"
    exit 1
fi

# Test build (dry run)
echo -e "${YELLOW}📋 Testing Docker build (dry run)...${NC}"
if docker build --dry-run . &> /dev/null; then
    echo -e "${GREEN}✅ Docker build test passed${NC}"
else
    echo -e "${RED}❌ Docker build test failed${NC}"
    exit 1
fi

# Test production build (dry run)
echo -e "${YELLOW}📋 Testing production Docker build (dry run)...${NC}"
if docker build --dry-run -f Dockerfile.prod . &> /dev/null; then
    echo -e "${GREEN}✅ Production Docker build test passed${NC}"
else
    echo -e "${RED}❌ Production Docker build test failed${NC}"
    exit 1
fi

# Check environment files
echo -e "${YELLOW}📋 Checking environment configuration...${NC}"
if [ -f ".env.example" ]; then
    echo -e "${GREEN}✅ Environment example file exists${NC}"
else
    echo -e "${YELLOW}⚠️  Environment example file not found${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Environment file exists${NC}"
else
    echo -e "${YELLOW}⚠️  Environment file not found (copy from .env.example)${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}🎉 Docker validation completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Copy .env.example to .env and configure your settings"
echo "2. Run 'docker-compose up -d' for local development"
echo "3. Run 'docker-compose -f docker-compose.prod.yml up -d' for production"
echo "4. Access the API at http://localhost:8080"
echo "5. View API docs at http://localhost:8080/docs"
echo ""
echo -e "${GREEN}✅ Your Docker setup is ready for deployment!${NC}"
