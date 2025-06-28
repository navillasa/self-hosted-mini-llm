#!/bin/bash
set -euo pipefail

# --- SETTINGS ---
LLM_USER=${1:-llmuser}  # default to 'llmuser' if no argument given
MODEL_DIR="$HOME/.cache/gpt4all"
MODEL_FILE="Meta-Llama-3-8B-Instruct.Q4_0.gguf"
MODEL_URL="https://gpt4all.io/models/gguf/$MODEL_FILE"
MODEL_DIR="/home/llmuser/.cache/gpt4all"

# --- FUNCTIONS ---

install_docker() {
  echo "🐳 Docker not found. Installing Docker..."
  sudo apt update
  sudo apt install -y ca-certificates curl gnupg lsb-release

  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/$(. /etc/os-release && echo "$ID")/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$(. /etc/os-release && echo "$ID") \
    $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

  sudo apt update
  sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

  echo "✅ Docker installed."
}

add_user_to_docker_group() {
  if groups $USER | grep -q '\bdocker\b'; then
    echo "👤 User already in 'docker' group."
  else
    echo "➕ Adding $USER to docker group..."
    sudo usermod -aG docker $USER
    echo "⚠️ Please log out and back in (or run 'newgrp docker') for group changes to take effect."
  fi
}

install_docker_compose() {
  echo "🔍 Checking for Docker Compose..."
  if ! docker compose version &> /dev/null; then
    echo "⚙️ Installing Docker Compose v2 plugin..."
    DOCKER_CLI_PLUGINS_DIR="/usr/lib/docker/cli-plugins"
    sudo mkdir -p "$DOCKER_CLI_PLUGINS_DIR"
    sudo curl -SL https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-linux-x86_64 \
      -o "$DOCKER_CLI_PLUGINS_DIR/docker-compose"
    sudo chmod +x "$DOCKER_CLI_PLUGINS_DIR/docker-compose"
    echo "✅ Docker Compose installed."
  else
    echo "✅ Docker Compose already installed."
  fi
}

download_model() {
  echo "🧠 Checking for model..."
  mkdir -p "$MODEL_DIR"
  cd "$MODEL_DIR"

  if [ -f "$MODEL_FILE" ]; then
    echo "✅ Model already exists at $MODEL_DIR/$MODEL_FILE. Skipping download."
  else
    echo "📥 Downloading model..."
    wget "$MODEL_URL"
    echo "✅ Model downloaded."
  fi
}

start_llm_container() {
  echo "🚀 Starting LLM node..."

  # Assume we are either in or next to llm-node dir
  if [ -f "docker-compose.yml" ]; then
    docker compose up -d --build
  elif [ -d "llm-node" ]; then
    cd llm-node
    docker compose up -d --build
  else
    echo "❌ Could not find llm-node directory or docker-compose.yml. Please run this from the right folder."
    exit 1
  fi

  echo "✅ Containers are starting in the background."
  echo "🔧 Check logs with: docker compose logs -f"
}

# --- MAIN ---

echo "🔐 Self-hosted Mini-LLM Bootstrap Starting..."

if ! command -v docker &> /dev/null; then
  install_docker
fi

add_user_to_docker_group
install_docker_compose
download_model
start_llm_container

echo "🎉 Done! Your LLM server should now be up and running."

