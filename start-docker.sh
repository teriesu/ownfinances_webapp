#!/bin/bash

# Finances Webapp - Quick Start Script

set -e

echo "🐳 Finances Webapp - Docker Setup"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file. Please edit it with your configuration."
        echo ""
        read -p "Do you want to edit .env now? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo "❌ .env.example not found. Cannot create .env file."
        exit 1
    fi
fi

echo ""
echo "🚀 Starting Docker containers..."
echo ""

# Stop existing containers if any
docker-compose down 2>/dev/null || true

# Build and start containers
docker-compose up -d --build

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run database migrations
echo "📦 Running database migrations..."
docker-compose exec -T web flask db upgrade

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Container status:"
docker-compose ps
echo ""
echo "🌐 Application is running at: http://localhost:616"
echo ""
echo "📝 Useful commands:"
echo "   View logs:           docker-compose logs -f"
echo "   Stop containers:     docker-compose down"
echo "   Restart:             docker-compose restart"
echo "   Database shell:      docker-compose exec db psql -U postgres -d personalfinances"
echo ""
echo "📖 For more information, see README.docker.md"
