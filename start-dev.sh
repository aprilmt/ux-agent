#!/bin/bash

# Development startup script
set -e

echo "🚀 Starting UX AI Agent in development mode..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup.sh first."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY is not set in .env file"
    exit 1
fi

echo "✅ Environment variables validated"

# Start services in development mode
echo "🔨 Starting development services..."
docker-compose -f docker-compose.yml up --build

echo "🎉 Development environment started!"
echo ""
echo "📱 Access your UX AI Agent:"
echo "   Frontend (Web UI): http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
