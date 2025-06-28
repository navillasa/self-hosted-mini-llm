#!/bin/sh
set -e

# Fix permissions if necessary (ignore errors if already correct)
chown -R llmuser:llmuser /home/llmuser/.cache/gpt4all || true

exec gosu llmuser "$@"
