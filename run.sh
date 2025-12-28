#!/bin/bash

echo "🚀 Starting Lyftr AI Full-Stack Scraper..."

# STOP if not using correct Python
PY_VERSION=$(python --version 2>&1)
if [[ "$PY_VERSION" != *"3.12"* ]]; then
  echo "❌ ERROR: Python 3.12 required. Found: $PY_VERSION"
  echo "👉 Run: pyenv activate lyftr_ai_312"
  exit 1
fi

echo "✅ Using $PY_VERSION"

echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "🎭 Installing Playwright browsers..."
playwright install

echo "🚀 Starting backend..."
uvicorn app.main:app --reload

