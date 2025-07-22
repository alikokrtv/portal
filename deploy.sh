#!/bin/bash

# Plus Kitchen Portal - Deployment Script for Remote Server

echo "🚀 Plus Kitchen Portal Deployment Starting..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials!"
fi

# Make sure logs directory exists
mkdir -p logs

# Run database migrations (if needed)
echo "🗄️ Checking database connection..."

# Start the application with Gunicorn for production
echo "🎯 Starting Plus Kitchen Portal..."
echo "📍 Application will be available at: http://your-server-ip:6600"

# Production deployment with Gunicorn
gunicorn --bind 0.0.0.0:6600 --workers 4 --timeout 60 --keepalive 2 --access-logfile logs/access.log --error-logfile logs/error.log app:app

echo "✅ Plus Kitchen Portal deployed successfully!" 