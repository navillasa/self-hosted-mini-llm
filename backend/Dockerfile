FROM python:3.11

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install llama-cpp-python with minimal CPU features (for Pentium J5005 compatibility)
# LLAMA_NATIVE=OFF prevents auto-detection of CPU features
# --no-binary forces building from source instead of using prebuilt wheels
RUN CMAKE_ARGS="-DLLAMA_NATIVE=OFF -DLLAMA_AVX=OFF -DLLAMA_AVX2=OFF -DLLAMA_AVX512=OFF -DLLAMA_FMA=OFF -DLLAMA_F16C=OFF" \
    pip install --no-cache-dir --no-binary :all: llama-cpp-python

# Install other requirements
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

# Change ownership of app dir to non-root user
RUN chown -R 1000:1000 /app

USER 1000

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
