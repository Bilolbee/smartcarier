#!/bin/bash
# Render.com Build Script for Backend
# Bu script Render.com'da build vaqtida ishlaydi

set -e  # Xatolik bo'lsa to'xtatish

echo "🚀 Starting backend build..."

# Python version tekshirish
python --version

# Dependencies install
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

echo "✅ Build completed successfully!"

