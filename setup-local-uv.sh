#!/bin/bash
# Setup script for local development with uv

set -e

echo "🚀 Setting up Finances Webapp with uv"
echo "======================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed!"
    echo ""
    echo "⚠️  Please restart your terminal or run:"
    echo "   source ~/.bashrc  (or ~/.zshrc)"
    echo ""
    exit 0
fi

echo "✅ uv is installed: $(uv --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv

# Activate instructions
echo ""
echo "✅ Virtual environment created!"
echo ""
echo "📝 To activate it, run:"
echo "   source .venv/bin/activate"
echo ""
echo "📦 To install dependencies:"
echo "   uv pip sync"
echo ""
echo "🚀 To run the app:"
echo "   flask run"
