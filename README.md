# 🧠 Self-Hosted GPT4All LLM API

A lightweight, self-hosted LLM server using [GPT4All-J](https://gpt4all.io/index.html), running entirely on CPU.

---

## 🛠️ What This Project Does

* Provisions a VPS with Terraform
* Hosts a quantized LLM model using `gpt4all`
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

## 🚀 How to Run

### 1. Provision the Server (Locally)

Run the Terraform code in the `modules/` directory to create a VPS on Hetzner:

```bash
cd modules
terraform init
terraform apply
```
Once it's done, take note of the server's public IP.

### 2. Copy the App Code to the Server

Transfer just the llm-node/ directory to your new VPS:
```
scp -r llm-node/ root@your.server.ip:~/
```
Alternatively, you could clone this repo on the server and use only the llm-node folder.

### 3. SSH to server and add [basic setup](https://github.com/navillasa/basic-vps-setup/blob/main/first-setup.sh).
```
ssh root@your.server.ip

# A fun cool helper script.
curl -sSL https://raw.githubusercontent.com/navillasa/basic-vps-setup/main/first-setup.sh | bash
```

### 4. Run `setup-llm.sh`.
### 5. Test the API.
Once the server is running, you can test it like this.
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

## 🔮 Next Steps

* [ ] Add reverse proxy (Traefik) for HTTPS + auth
* [ ] Add logging & basic monitoring (Prometheus + Grafana)
* [ ] Write CI tests to validate API response
* [ ] Auto-deploy updates via CI/CD
* [ ] Serve via domain name with TLS
