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

## 💼 DevOps Highlights

### Infrastructure as Code
- **Terraform modules** for reproducible VPS provisioning
- **Automated DNS** and SSL certificate management
- **Cost optimization**: ~$5/month for full AI inference capability

### Production Readiness
- **Health checks** and graceful error handling
- **Prometheus metrics** for comprehensive monitoring
- **Basic authentication** for API security
- **Automated deployment** with Docker Compose

### Operational Excellence
- **Zero-downtime deployments** via container orchestration
- **Real-time monitoring** with Grafana dashboards
- **Resource tracking** (CPU, memory, inference latency)
- **Performance analytics** (request rates, error rates, token generation)
- **Documentation-driven** infrastructure management

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

### Grafana Dashboard
Access the monitoring dashboard at `https://monitoring.your-domain.com`:
- **API Performance**: Request rates, response times, error rates
- **System Resources**: CPU, memory, and storage utilization
- **Model Metrics**: Inference latency and token generation rates
- **Business Metrics**: Cost per request and usage patterns

### Resource Usage
- **Memory**: ~4GB RAM for 8B parameter model
- **CPU**: Intel/AMD x64 (no GPU required)
- **Storage**: ~5GB for model artifacts
- **Network**: <1MB/s typical inference load

### Response Times
- **Cold start**: 2-3 seconds (model loading)
- **Warm inference**: 200-500ms per token (CPU-only, quite slow!)
- **Concurrent requests**: 2-4 optimal (single CPU core limitation)

### Cost Analysis
```
Monthly Operating Costs:
├── Hetzner VPS (CX21): $5.00/month
├── Domain name: $1.00/month
├── SSL Certificate: $0.00 (Let's Encrypt)
└── Total: ~$6.00/month

Cost per 1000 tokens: <$0.001
(vs OpenAI GPT-3.5: $0.002/1000 tokens)
```

## 🔒 Security Considerations

### Implemented
- ✅ HTTPS-only communication (Let's Encrypt)
- ✅ HTTP Basic Authentication
- ✅ Firewall configuration (UFW)
- ✅ Container isolation
- ✅ No model data logging
- ✅ Input validation and sanitization

### Future Enhancements
- [ ] Rate limiting and DDoS protection
- [ ] API key-based authentication
- [ ] Request audit logging
- [ ] WAF integration (Cloudflare)

## 🎯 DevOps Best Practices Demonstrated

### 1. Infrastructure as Code
```hcl
# Terraform module structure
modules/
├── hetzner_instance/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── main.tf
└── terraform.tfvars
```

### 2. Containerization Strategy
```dockerfile
# Multi-stage build for optimization
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3. Configuration Management
```yaml
# Docker Compose with environment separation
services:
  llm-api:
    build: .
    environment:
      - MODEL_NAME=${MODEL_NAME}
      - MAX_TOKENS=${MAX_TOKENS}
    volumes:
      - model_cache:/root/.cache/gpt4all
```

## 📈 Scaling Considerations

### Current Limitations
- Single-node deployment (no horizontal scaling)
- CPU-only inference (significantly slower than GPU setups)
- Small quantized model (limited reasoning capability vs GPT-4)
- Stateful model loading (no shared cache)
- Not suitable for production traffic (demo/learning purposes)

### Scaling Roadmap
1. **Load balancing** with multiple API instances
2. **GPU acceleration** for faster inference
3. **Model serving optimization** (ONNX, TensorRT)
4. **Kubernetes deployment** for container orchestration
5. **Distributed caching** for model artifacts

## 🚧 Future Enhancements

### Monitoring & Observability
- [x] **Prometheus metrics export** (API performance, system resources)
- [x] **Grafana dashboards** (real-time monitoring and alerting)
- [ ] Request tracing with OpenTelemetry
- [ ] Log aggregation (ELK stack)

### CI/CD Pipeline
- [ ] GitHub Actions for automated testing
- [ ] Container vulnerability scanning
- [ ] Automated deployment on code changes
- [ ] Infrastructure drift detection

### Advanced Features
- [ ] Model hot-swapping without downtime
- [ ] Multi-model support (model routing)
- [ ] Request queuing and batching
- [ ] Auto-scaling based on load

## 📚 Learning Outcomes

This project demonstrates proficiency in:

- **Cloud Infrastructure**: Terraform, VPS management, DNS configuration
- **Containerization**: Docker best practices, multi-stage builds, compose orchestration
- **API Design**: FastAPI, async programming, error handling, documentation
- **DevOps**: Infrastructure as Code, configuration management, deployment automation
- **Security**: HTTPS, authentication, container security, firewall configuration
- **Cost Optimization**: Resource sizing, efficient architecture, budget management

## 🔗 Related Projects

- **[TV Dashboard K8s](https://github.com/navillasa/tv-dashboard-k8s)**: Full-stack Kubernetes deployment with GitOps
- **[VPN Ad Blocker](https://github.com/navillasa/vpn-ad-blocker)**: Network security and automation
- **[Basic VPS Setup](https://github.com/navillasa/basic-vps-setup)**: Server hardening and initial configuration

---

**Built by Natalie Villasana** • [Portfolio](https://navillasa.dev) • [LinkedIn](https://linkedin.com/in/natalievillasana)