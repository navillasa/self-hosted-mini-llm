# 🧠 Self-Hosted Mini LLM

[![CI/CD](https://github.com/navillasa/self-hosted-mini-llm/actions/workflows/ci.yml/badge.svg)](https://github.com/navillasa/self-hosted-mini-llm/actions/workflows/ci.yml)
[![Security Scan](https://github.com/navillasa/self-hosted-mini-llm/actions/workflows/security.yml/badge.svg)](https://github.com/navillasa/self-hosted-mini-llm/actions/workflows/security.yml)
[![Lint](https://github.com/navillasa/self-hosted-mini-llm/actions/workflows/lint.yml/badge.svg)](https://github.com/navillasa/self-hosted-mini-llm/actions/workflows/lint.yml)

> **Full-stack AI chat application with GitOps deployment to Kubernetes**

An LLM chat application with GitHub OAuth, automated deployment with ArgoCD, and custom-compiled llama.cpp for running on legacy hardware (aka [my homelab's](https://github.com/navillasa/kubernetes-homelab) Pentium J5005 processor).

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   GitHub    │────▶│   ArgoCD     │────▶│   MicroK8s      │
│   (Source)  │     │   (GitOps)   │     │   Homelab       │
└─────────────┘     └──────────────┘     └─────────────────┘
                                                   │
                          ┌────────────────────────┼─────────────────┐
                          │                        │                 │
                   ┌──────▼──────┐        ┌───────▼──────┐   ┌─────▼──────┐
                   │  Frontend   │        │   Backend    │   │   Vault    │
                   │  (React)    │───────▶│   (FastAPI)  │◀──│  (Secrets) │
                   │  nginx:8080 │        │   GPT4All    │   └────────────┘
                   └─────────────┘        └──────────────┘
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Orchestration** | Kubernetes (MicroK8s) | Container orchestration on homelab |
| **GitOps** | ArgoCD | Automated deployment from Git |
| **Manifests** | Kustomize | Environment-specific configurations |
| **CI/CD** | GitHub Actions | Automated testing and image builds |
| **Container Registry** | GitHub Container Registry (ghcr.io) | Docker image storage |
| **Secrets** | HashiCorp Vault + External Secrets Operator | Secure secret management |
| **Frontend** | React + Vite | Modern SPA with TypeScript |
| **Backend** | FastAPI + Uvicorn | High-performance async API |
| **AI Model** | GPT4All (Llama 3 8B) | Local LLM inference |
| **Auth** | GitHub OAuth 2.0 + JWT | User authentication |
| **Monitoring** | Prometheus | Metrics collection |


## 📦 Repository Structure

```
.
├── backend/                # FastAPI backend
│   ├── main.py            # API endpoints and LLM integration
│   ├── auth.py            # GitHub OAuth + JWT auth
│   ├── rate_limiter.py    # Request rate limiting
│   └── Dockerfile         # Backend container image
├── frontend/              # React frontend
│   ├── src/               # React components
│   ├── nginx.conf         # nginx configuration (port 8080)
│   └── Dockerfile         # Frontend container image
├── k8s/                   # Kubernetes manifests
│   ├── base/              # Base resources (deployments, services, secrets)
│   ├── overlays/dev/      # Dev environment overlay
│   └── argocd/            # ArgoCD Application definitions
└── .github/workflows/     # CI/CD pipelines
    └── ci.yml             # Build, test, and publish images
```

## 🏃 Deployment

### Prerequisites

- Kubernetes cluster (tested on MicroK8s)
- ArgoCD installed
- Vault + External Secrets Operator configured
- GitHub OAuth app credentials

### Setup Secrets in Vault

```bash
vault kv put secret/mini-llm/backend \
  github_client_id='your-client-id' \
  github_client_secret='your-client-secret' \
  jwt_secret="$(openssl rand -base64 32)" \
  frontend_url='https://your-frontend-url'
```

### Deploy with ArgoCD

```bash
# Apply the ArgoCD Application
kubectl apply -f k8s/argocd/mini-llm-app-dev.yaml

# Watch deployment
kubectl get application -n argocd mini-llm-dev
kubectl get pods -n mini-llm-dev -w
```

### Manual Deployment (without ArgoCD)

```bash
# Apply manifests directly
kubectl apply -k k8s/overlays/dev

# Check status
kubectl get all -n mini-llm-dev
```

## 🔄 CI/CD Pipeline

When you push to `main`:

1. **Run Tests**: Backend unit tests + frontend build tests
2. **Build Images**: Docker images tagged with git commit SHA
3. **Push to Registry**: Images pushed to ghcr.io
4. **Update Kustomization**: Image tags automatically updated in git
5. **ArgoCD Sync**: Detects changes and deploys new version

## 📊 Monitoring

Prometheus metrics available at `/metrics`:

- `llm_requests_total` - API request counts
- `llm_request_duration_seconds` - Request latency
- `llm_inference_duration_seconds` - Model inference time
- `llm_tokens_generated_total` - Total tokens generated
- `llm_model_loaded` - Model status
- `llm_cpu_usage_percent` - CPU utilization
- `llm_memory_usage_bytes` - Memory usage
- `llm_auth_requests_total` - OAuth attempts
- `llm_rate_limit_hits_total` - Rate limit violations

## 🔐 Security Features

- **Non-root containers**: Both frontend and backend run as user 1000
- **Secret management**: Vault integration, no secrets in git
- **OAuth authentication**: GitHub social login
- **JWT tokens**: Stateless authentication
- **Rate limiting**: Prevents abuse
- **HTTPS**: TLS termination at ingress

## 🛠️ Local Development

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and configure .env
cp .env.example .env

# Run backend
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install

# Copy and configure .env
cp .env.example .env

# Run dev server
npm run dev
```

## 🐛 Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -n mini-llm-dev

# View logs
kubectl logs -n mini-llm-dev deployment/backend
kubectl logs -n mini-llm-dev deployment/frontend

# Check events
kubectl describe pod -n mini-llm-dev <pod-name>
```

### ArgoCD not syncing

```bash
# Check application status
kubectl get application -n argocd mini-llm-dev -o yaml

# Force sync
argocd app sync mini-llm-dev
```

### Secrets not available

```bash
# Check ExternalSecret
kubectl get externalsecret -n mini-llm-dev
kubectl describe externalsecret backend-secrets -n mini-llm-dev

# Verify Vault connection
kubectl get clustersecretstore vault-backend
```

## 🔗 Related Projects

- **[Homelab Infrastructure](https://github.com/navillasa/homelab)**: MicroK8s homelab with Vault, ArgoCD, monitoring
- **[TV Dashboard K8s](https://github.com/navillasa/tv-dashboard-k8s)**: Full-stack app with multi-cloud deployment
- **[Multi-cloud LLM Router](https://github.com/navillasa/multi-cloud-llm-router)**: Enterprise LLM routing and cost optimization
