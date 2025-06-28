FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add a non-root user
RUN adduser --disabled-password --gecos '' llmuser

RUN chown -R llmuser:llmuser /app

RUN mkdir -p /home/llmuser/.cache/gpt4all && chown -R llmuser:llmuser /home/llmuser/.cache

# Need gosu utility in order to drop from root to llmuser in entrypoint
RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
