# Use an official Python runtime as a base image
FROM python:3-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
    iproute2 \
    libgl1 \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    curl \
    tmux \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install ngrok
RUN curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && \
    echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && apt-get install -y ngrok

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mtcnn
RUN pip install --no-cache-dir facenet-pytorch --no-deps

# Copy application code
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Configure ngrok (use environment variable or default)\n\
if [ -n "$NGROK_AUTHTOKEN" ]; then\n\
    ngrok config add-authtoken "$NGROK_AUTHTOKEN"\n\
else\n\
    echo "Warning: NGROK_AUTHTOKEN environment variable not set"\n\
fi\n\
\n\
echo ":: Starting Unilever AI server locally ..."\n\
\n\
# Check if tmux session already exists\n\
if tmux has-session -t deploy 2>/dev/null; then\n\
    echo "==>> Stopping existing tmux session '\''deploy'\''"\n\
    tmux kill-session -t deploy\n\
fi\n\
\n\
# Start backend server\n\
tmux new-session -d -s deploy "python UBL_API.py"\n\
\n\
# Wait for local server to be ready\n\
echo ":: Waiting for server to respond on http://127.0.0.1:5656/status ..."\n\
timeout=500\n\
elapsed=0\n\
interval=5\n\
\n\
while true; do\n\
    status_code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5656/status || echo 000)\n\
    if [[ "$status_code" == "200" ]]; then\n\
        echo "==>> AI Local Server is up (HTTP 200)"\n\
        break\n\
    fi\n\
    if [[ "$elapsed" -ge "$timeout" ]]; then\n\
        echo "ERROR: Local server failed to start in $timeout seconds"\n\
        exit 1\n\
    fi\n\
    sleep $interval\n\
    elapsed=$((elapsed + interval))\n\
    echo "Still waiting... ($elapsed/$timeout sec) - Last status: $status_code"\n\
done\n\
\n\
# Kill old ngrok if running\n\
pkill -f "ngrok http" || true\n\
\n\
# Start ngrok in tmux\n\
echo "==>> Starting ngrok tunnel..."\n\
tmux new-window -t deploy "ngrok http --domain=he.ngrok.app 5656"\n\
\n\
# Check ngrok process is running\n\
echo ":: Waiting for ngrok process to start ..."\n\
sleep 5\n\
elapsed=0\n\
while true; do\n\
    if pgrep -f "ngrok http" >/dev/null; then\n\
        echo "==>> ngrok process is running (verified)"\n\
        break\n\
    fi\n\
    if [[ "$elapsed" -ge "$timeout" ]]; then\n\
        echo "ERROR: ngrok did not start in $timeout seconds"\n\
        exit 1\n\
    fi\n\
    sleep $interval\n\
    elapsed=$((elapsed + interval))\n\
    echo "Still waiting... ($elapsed/$timeout sec)"\n\
    tmux new-window -t deploy "ngrok http --domain=he.ngrok.app 5656"\n\
    sleep 5\n\
done\n\
\n\
# Wait for ngrok tunnel to be available\n\
echo ":: Waiting for server to respond on https://he.ngrok.app/status ..."\n\
elapsed=0\n\
while true; do\n\
    status_code=$(curl -s -o /dev/null -w "%{http_code}" https://he.ngrok.app/status || echo 000)\n\
    if [[ "$status_code" == "200" ]]; then\n\
        echo "==>> AI ngrok Server is up (HTTP 200)"\n\
        break\n\
    fi\n\
    if [[ "$elapsed" -ge "$timeout" ]]; then\n\
        echo "ERROR: ngrok tunnel failed to respond in $timeout seconds"\n\
        exit 1\n\
    fi\n\
    sleep $interval\n\
    elapsed=$((elapsed + interval))\n\
    echo "Still waiting... ($elapsed/$timeout sec) - Last status: $status_code"\n\
done\n\
\n\
# Final confirmation\n\
echo "==>> ngrok is connected to the local server"\n\
echo "Unilever Local Server started Successfully !!!"\n\
echo "Local AI server and ngrok started successfully"\n\
echo "==================================>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>=================================="\n\
echo "Starting the Monitoring Script..."\n\
ps -aux | grep -E "UBL_API|ngrok|python" | grep -v grep\n\
\n\
# Keep container running\n\
while true; do\n\
    sleep 60\n\
done' > /app/start.sh && chmod +x /app/start.sh

# Expose the application port
EXPOSE 5656

# Set environment variables
ENV NGROK_AUTHTOKEN=2lPN9d5cdnGlSrWb4JGEGVI1Mah_4bvvrGdKKU2ME7nkck8L7

# Start the application
CMD ["/app/start.sh"]