FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Set HOME for the non-root user
ENV HOME=/home/appuser
ENV XDG_CACHE_HOME=/home/appuser/.cache

# Make sure cache dir exists and is owned by non-root
RUN mkdir -p $XDG_CACHE_HOME/gpt4all && chown -R 1000:1000 /home/appuser

USER 1000

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
