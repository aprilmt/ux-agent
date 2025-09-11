#!/bin/bash

# UX AI Agent Setup Script
set -e

echo "🚀 Setting up UX AI Agent..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
    echo "   Required: OPENAI_API_KEY, SECRET_KEY"
    echo "   Optional: Stripe keys for payment integration"
    echo ""
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres
mkdir -p data/redis

# Set permissions
echo "🔐 Setting permissions..."
chmod +x deploy.sh
chmod +x setup.sh

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run ./deploy.sh to start the application"
echo ""
echo "🔑 Required environment variables:"
echo "   - OPENAI_API_KEY: Your OpenAI API key"
echo "   - SECRET_KEY: A secret key for JWT tokens"
echo ""
echo "💳 Optional environment variables (for payments):"
echo "   - STRIPE_PUBLISHABLE_KEY: Your Stripe publishable key"
echo "   - STRIPE_SECRET_KEY: Your Stripe secret key"
echo "   - STRIPE_WEBHOOK_SECRET: Your Stripe webhook secret"
