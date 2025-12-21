# 🧠 Self-Hosted LLM Infrastructure

> **Small-scale AI inference setup using Terraform, Docker, and FastAPI**

A lightweight demonstration of DevOps practices for hosting a quantized LLM on a single VPS, showcasing infrastructure automation, containerization, and API design patterns that could scale to larger deployments.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-llm.navillasa.dev-blue)](https://llm.navillasa.dev)
[![Infrastructure](https://img.shields.io/badge/Infrastructure-Terraform-purple)](./modules/)
[![API](https://img.shields.io/badge/API-FastAPI-green)](./llm-node/)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Internet      │───▶│   Traefik        │───▶│   FastAPI       │
│   (HTTPS)       │    │   Reverse Proxy  │    │   + GPT4All     │
└─────────────────┘    │   + Let's Encrypt│    │   (Container)   │
                       └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │   Hetzner VPS    │
                       │   (Terraform)    │
                       │   Ubuntu 22.04   │
                       └──────────────────┘
```

### Key Components

- **Infrastructure**: Hetzner Cloud VPS provisioned via Terraform
- **Model**: Meta Llama 3 8B (4-bit quantized) via GPT4All
- **API**: FastAPI with Pydantic validation and error handling
- **Reverse Proxy**: Traefik with automatic HTTPS (Let's Encrypt)
- **Security**: HTTP Basic Auth, firewall configuration
- **Containerization**: Docker Compose for local development and production

## 🚀 Live Demo

**Public API Endpoint**: https://llm.navillasa.dev

```bash
# Test the live API
curl -u demo:password -X POST https://llm.navillasa.dev/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explain DevOps in 50 words", "max_tokens": 100}'
```

**Response Example**:
```json
{
  "response": "DevOps combines development and operations to streamline software delivery. It emphasizes automation, continuous integration/deployment, infrastructure as code, monitoring, and collaboration. Key tools include Docker, Kubernetes, Terraform, and CI/CD pipelines. DevOps reduces deployment time, increases reliability, and enables faster iteration cycles."
}
```

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Infrastructure** | Terraform + Hetzner Cloud | Automated VPS provisioning |
| **Containerization** | Docker + Docker Compose | Application packaging and orchestration |
| **Web Framework** | FastAPI + Uvicorn | High-performance async API |
| **AI Model** | GPT4All (Llama 3 8B Q4) | Local inference without external APIs |
| **Reverse Proxy** | Traefik | HTTPS termination and routing |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Security** | Let's Encrypt + Basic Auth | SSL certificates and API protection |

## 🏃‍♂️ Quick Start

### Prerequisites
- Terraform >= 1.0
- Docker and Docker Compose
- Domain name with DNS access
- Hetzner Cloud account

### 1. Provision Infrastructure
```bash
# Clone the repository
git clone https://github.com/navillasa/self-hosted-mini-llm.git
cd self-hosted-mini-llm

# Configure Terraform variables
cp modules/terraform.tfvars.example modules/terraform.tfvars
# Edit terraform.tfvars with your Hetzner API token

# Deploy infrastructure
cd modules
terraform init
terraform apply
```

### 2. Deploy Application
```bash
# SSH to your server
ssh root@your-server-ip

# Clone repo on server
git clone https://github.com/navillasa/self-hosted-mini-llm.git
cd self-hosted-mini-llm/llm-node

# Configure environment
cp .env.example .env
# Edit .env with your domain and auth credentials

# Deploy application
chmod +x setup-llm.sh
./setup-llm.sh
```

### 3. Verify Deployment
```bash
# Health check
curl https://your-domain.com/health

# Test inference
curl -u username:password -X POST https://your-domain.com/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!", "max_tokens": 50}'
```

## 📊 Performance & Monitoring

### Available Metrics
The API exports the following Prometheus metrics:
- `llm_requests_total` - Total API requests by endpoint and status
- `llm_request_duration_seconds` - Request duration histogram
- `llm_inference_duration_seconds` - Model inference time
- `llm_tokens_generated_total` - Cumulative tokens generated
- `llm_model_loaded` - Model availability status (0/1)
- `llm_cpu_usage_percent` - Real-time CPU utilization
- `llm_memory_usage_bytes` - Memory consumption

## 🔗 Related Projects

- **[TV Dashboard K8s](https://github.com/navillasa/tv-dashboard-k8s)**: Full-stack Kubernetes deployment with GitOps
- **[VPN Ad Blocker](https://github.com/navillasa/vpn-ad-blocker)**: Network security and automation
- **[Basic VPS Setup](https://github.com/navillasa/basic-vps-setup)**: Server hardening and initial configuration
