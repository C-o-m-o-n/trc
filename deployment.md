# Deployment Guide: TRC Mission Control 🛰️🏗️🦾

TRC (Terminal Relay Controller) is designed to be a lightweight, "Always-On" technical guardian. This guide explains how to deploy TRC in professional environments.

## 🐳 Option 1: Docker (Team Command Center)
The fastest way to deploy TRC for a technical team.

1.  **Configure**: Create a `.env` file with your `GEMINI_API_KEY`.
2.  **Launch**:
    ```bash
    docker-compose up -d
    ```
3.  **Access**:
    ```bash
    docker attach trc-mission-control
    ```
    *Note: Docker volumes ensure that technical history (`trc_history.db`) persists across container restarts.*

## 🍓 Option 2: Raspberry Pi (Edge Listener)
Transform a Raspberry Pi into a 24/7 "Headless Technical Watcher."

1.  **Clone** the repo onto your Pi.
2.  **Run the setup script**:
    ```bash
    chmod +x scripts/setup_pi.sh
    ./scripts/setup_pi.sh
    ```
3.  **Monitor**:
    - The `trc.service` will start automatically on boot.
    - AI `Monitor Mode` (Phase 2.7) will watch his background relays even when you are logged off.
    - Check service health: `systemctl status trc.service`

## 🧩 Strategic Overview: The Zero-Footprint Registry
TRC deployment is unique because it requires **no central server**.
- **Real-time Routing**: Handled by PubNub.
- **Technical Memory**: Local SQLite (edge-native).
- **Intelligence**: Gemini Cloud Inference.

This means you can deploy a TRC "Listener" in a remote server room, and as long as it has internet, it can act as a **Proactive Incident Commander** for your team globally. 🛰️🦾
