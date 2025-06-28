#!/bin/sh
set -e
chown -R llmuser:llmuser /home/llmuser/.cache/gpt4all || true
exec "$@"
