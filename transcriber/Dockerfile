# Use NVIDIA CUDA base image for GPU support
FROM nvidia/cuda:12.1.0-base-ubuntu22.04

WORKDIR /app

# Install Python 3.11 and system dependencies
RUN apt-get update && apt-get install -y     python3.11     python3-pip     ffmpeg     git     curl     && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 &&     update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Install Node.js (for supergateway)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&     apt-get install -y nodejs

# Install Supergateway globally
RUN npm install -g supergateway

# Install Python dependencies including cuDNN
RUN pip install --no-cache-dir     "mcp[cli]"     yt-dlp     faster-whisper     ffmpeg-python     nvidia-cudnn-cu12

# Set library path for cuDNN
ENV LD_LIBRARY_PATH=/usr/local/lib/python3.11/dist-packages/nvidia/cudnn/lib:$LD_LIBRARY_PATH

# Copy server code
COPY server.py /app/server.py

# Entrypoint: Run supergateway wrapping the python server
CMD ["npx", "supergateway", "--port", "8080", "--stdio", "python server.py"]
