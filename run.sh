#!/bin/bash

# Stock Exchange Board API - Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Stock Exchange Board API - Starting up...${NC}"

# Check if .env file exists, if not create it from .env.example
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your configuration${NC}"
fi

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt

# Run migrations (if using Alembic)
# echo -e "${GREEN}Running database migrations...${NC}"
# alembic upgrade head

# Run tests
echo -e "${GREEN}Running tests...${NC}"
pytest tests/ -v --cov=app --cov-report=html || true

# Start the API server
echo -e "${GREEN}Starting FastAPI server...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo -e "${GREEN}API server stopped${NC}"
