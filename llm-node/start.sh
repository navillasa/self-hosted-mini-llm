#!/bin/bash
set -euo pipefail

echo "🔍 Checking for docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install Docker Compose."
    exit 1
fi

echo "🚀 Starting LLM node with Docker Compose..."
docker-compose up -d --pull always

echo "✅ Containers are starting in the background."

echo
echo "🔧 You can check logs with:"
echo "   docker-compose logs -f"
echo
echo "🧠 If this is your first time, it may take a few minutes to download the model from Hugging Face."
echo "   Make sure your .env file contains a valid HUGGINGFACE_TOKEN."

echo
echo "🌐 Once running, access your LLM endpoint at:"
echo "   http://localhost:11434/v1/chat/completions"

