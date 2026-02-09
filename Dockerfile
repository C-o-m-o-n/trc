# Use a lightweight Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements or just install directly if requirements.txt doesn't exist
# For TRC, we know we need: requests, google-genai, python-dotenv
RUN pip install --no-cache-dir requests google-genai python-dotenv pubnub

# Copy project files
COPY . .

# Environment variables (Defaults)
ENV PYTHONUNBUFFERED=1

# TRC relies on .env for the API key, but we can also pass it via Docker ENV
# VOLUME /app/data # For SQLite persistence if we move database path

# Run the chat client
# Note: For headless mode, we might want a different entrypoint in the future
CMD ["python", "chat.py"]
