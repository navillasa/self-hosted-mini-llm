# 🧠 Self-Hosted GPT4All LLM API

A lightweight, self-hosted LLM server using [GPT4All-J](https://gpt4all.io/index.html), running entirely on CPU.

---

## 🛠️ What This Project Does

* Provisions a VPS with Terraform
* Hosts a quantized LLM model using `gpt4all` (CPU-only)
* Wraps the model with a REST API via FastAPI
* Accepts text prompts and returns completions
* Fully self-contained, offline-capable, no OpenAI dependency

---

## Current Setup

1. Hetzner VPS provisioned via Terraform
2. Model downloaded to `~/.cache/gpt4all`
3. FastAPI app containerized with Docker
4. Model + API served together via `docker-compose`

---

## Example Request

```bash
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```

Response:

```json
{"response":"The capital of France is Paris."}
```

---

## How to Run

1. Download the model:

```bash
mkdir -p ~/.cache/gpt4all
cd ~/.cache/gpt4all
wget https://gpt4all.io/models/gguf/Meta-Llama-3-8B-Instruct.Q4_0.gguf
```

2. Clone the repo and start containers:

```bash
git clone https://github.com/navillasa/self-hosted-mini-llm.git
cd self-hosted-mini-llm/llm-node
docker-compose up -d --build
```

---

## 🔮 Next Steps

* [ ] Add reverse proxy (Traefik) for HTTPS + auth
* [ ] Add logging & basic monitoring (Prometheus + Grafana)
* [ ] Write CI tests to validate API response
* [ ] Auto-deploy updates via CI/CD
* [ ] Serve via domain name with TLS
