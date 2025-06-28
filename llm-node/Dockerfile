FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add a non-root user
RUN adduser --disabled-password --gecos '' llmuser

RUN chown -R llmuser:llmuser /app

# Run as non-root user
USER llmuser

RUN mkdir -p /home/llmuser/.cache && chown -R llmuser:llmuser /home/llmuser/.cache

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
