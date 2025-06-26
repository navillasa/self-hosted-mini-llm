# Self-Hosted GPT4All-J LLM Server

Deploy the GPT4All-J, a lightweight open-source LLM optimized for CPU, locally using Docker and Hetzner VPS.

---

## Overview

* Provision Hetzner VPS with Terraform
* Run the model in Docker using the `vllm/vllm-openai` image
* Serve the model with an OpenAI-compatible API on port 8000

---

## Setup So Far

1. Created Hetzner server with Terraform
2. Wrote `docker-compose.yml` to run the model
3. Tested basic API with curl requests


To run:

```bash
docker-compose up -d
```

The GPT4All API will be available at `http://your_server_ip:8080`.

## Notes

* Cached models will be stored in `~/.cache/gpt4all` on your host machine.
* Check the container logs for startup status:

```bash
docker logs -f gpt4all_j
```

## Next Steps

* Automate Docker install with Terraform
* Add reverse proxy (Traefik) for auth & HTTPS
* Setup Prometheus & Grafana for monitoring
* Implement CI/CD for updates
