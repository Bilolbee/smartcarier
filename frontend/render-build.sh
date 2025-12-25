#!/bin/bash
# Render.com Build Script for Frontend
# Bu script Render.com'da build vaqtida ishlaydi

set -e  # Xatolik bo'lsa to'xtatish

echo "🚀 Starting frontend build..."

# Node version tekshirish
node --version
npm --version

# Dependencies install
echo "📦 Installing dependencies..."
npm ci --production=false

# Build
echo "🏗️ Building Next.js application..."
npm run build

echo "✅ Build completed successfully!"

