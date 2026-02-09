#!/bin/bash

# TRC - Raspberry Pi Edge Setup Script
# Deploy your intelligent Mission Control as a 24/7 background listener.

echo "📡 Initializing TRC Edge Listener Setup..."

# 1. Update and install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git

# 2. Create virtual environment
echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install requests google-genai python-dotenv

# 3. Handle Environment Variables
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Please enter your GEMINI_API_KEY:"
    read api_key
    echo "GEMINI_API_KEY=$api_key" > .env
fi

# 4. Set up systemd service for Always-On monitoring
echo "⚙️ Registering TRC as a background service..."
PROJECT_DIR=$(pwd)
USER_NAME=$(whoami)

cat <<EOF | sudo tee /etc/systemd/system/trc.service
[Unit]
Description=Terminal Relay Controller (TRC) AI Service
After=network.target

[Service]
ExecStart=${PROJECT_DIR}/venv/bin/python ${PROJECT_DIR}/chat.py
WorkingDirectory=${PROJECT_DIR}
StandardOutput=inherit
StandardError=inherit
Restart=always
User=${USER_NAME}

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable trc.service

echo "✅ TRC setup complete!"
echo "🚀 To start TRC now: sudo systemctl start trc.service"
echo "📊 To view AI logs: journalctl -u trc.service -f"
