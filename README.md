# 🧠 Self-Hosted GPT4All LLM API

A lightweight, self-hosted LLM server using [GPT4All-J](https://gpt4all.io/index.html), running entirely on CPU.

## What This Project Does

* Provisions a VPS with Terraform
* Hosts a quantized LLM model using `gpt4all`
* Wraps the model with a REST API via FastAPI
* Accepts text prompts and returns completions
* Fully self-contained, offline-capable, no OpenAI dependency

## Current Setup

1. Hetzner VPS provisioned via Terraform
2. Model downloaded to `~/.cache/gpt4all`
3. FastAPI app containerized with Docker
4. Model + API served together via `docker-compose` with Traefik reverse proxy, HTTPS, and basic auth

## 👁️ Check Out the Public Instance

You can test the public instance at https://llm.navillasa.dev with basic auth:
```bash
curl -u user:pass -X POST https://llm.navillasa.dev/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What's inference?"}'
```

## How to Run Your Own Instance

### 1. Provision the Server

Run the Terraform code in the `modules/` directory to create a VPS on Hetzner:

```bash
cd modules
terraform init
terraform apply
```
Once it's done, take note of the server's public IP.

### 2. Copy or Clone the App Code to the Server
```
scp -r llm-node/ youruser@your.server.ip:~/
# OR on the server:
git clone https://github.com/navillasa/self-hosted-mini-llm.git
cd self-hosted-mini-llm/llm-node
```

### 3. SSH to server and run [basic setup](https://github.com/navillasa/basic-vps-setup/blob/main/first-setup.sh).
```
ssh youruser@your.server.ip

# A fun cool helper script.
curl -sSL https://raw.githubusercontent.com/navillasa/basic-vps-setup/main/first-setup.sh | bash
```

### 4. Configure Environment Variables
Before running, you must create an `.env` setting Terraform variables, domain configuration, Traefik auth info, and your model. See [.env.example](https://github.com/navillasa/self-hosted-mini-llm/blob/main/.env.example).

You must also update DNS records to point your domain to your server's public IP.

### 5. Run Setup Script
```
./setup-llm.sh
```
This will build and launch the Docker containers, download the model if needed, and start the API + Traefik reverse proxy.

### 5. Test the API locally.
Local test (inside your VPS).
```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```
Public test (replace with your domain and basic auth credentials):
```
curl -u yourdesiredusername:yourpassword -X POST https://your.domain.example/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is inference?"}'
```

## 🔮 Next Steps

* [ ] Add logging & basic monitoring (Prometheus + Grafana)
* [ ] Write CI tests to validate API response
* [ ] Auto-deploy updates via CI/CD
