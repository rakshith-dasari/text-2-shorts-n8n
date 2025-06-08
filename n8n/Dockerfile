FROM n8nio/n8n:latest

# Switch to root to install packages
USER root

# Install required packages
RUN apk add --no-cache --update \
    python3 \
    py3-pip \
    gcc \
    python3-dev \
    musl-dev \
    curl \
    ffmpeg \
    yt-dlp

# (Optional) Switch back to node user for runtime security
USER node

# Set working directory
WORKDIR /home/node

# Expose default n8n port
EXPOSE 5678

