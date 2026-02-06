# TRC (Terminal Relay Controller) 🛰️🧠🏗️

**"Beyond Chat: Intelligent Mission Control for Technical Teams"**

TRC is an AI-orchestrated communication middleware designed for DevOps, SRE, and Edge engineering teams. Built with Python and PubNub, TRC transforms raw technical relays into a **Mission Control Center** where Gemini 1.5 Flash acts as an active technical guardian and project manager.

---

## ✨ Orchestrated Features

### 🧠 The Intelligence Layer (Gemini 1.5 Flash)
- **Tool-Augmented Orchestration**: Gemini has "hands" to read/write local code and query technical history autonomously.
- **Proactive Monitor Mode**: Passively watches background relays and triggers **Autonomous Technical Alerts** if crashes or blockers are detected.
- **Vision Engine**: Analyze screenshots of errors directly in the terminal via `/analyze`.
- **Pulse Reports**: Cross-channel technical health summaries via `/pulse`.

### 📡 IRC Parity (Professional Coordination)
- **AI-Aware Topics**: `/topic` sets a mission context that informs Gemini's technical reasoning.
- **Persistent Identity**: Secure your handle with `/nick`, saved to a local SQLite settings table.
- **Private Consulting**: `/whisper` for one-on-one technical brainstorming with the AI Brain.
- **Presence Tracking**: See who is active in the relay network with `/who`.

---

## 🏗️ Architecture: The Intelligence Loop
TRC doesn't just sync messages; it creates a feedback loop between the network and the machine.
- **Listen**: PubNub Real-time Network.
- **Remember**: Local SQLite Persistence.
- **Reason**: Gemini 1.5 Flash Reasoning Engine.
- **Act**: Technical File Tools (Read/Write).

[View Full Architectural Diagram](research/architecture.md)

---

## 🚀 Getting Started

1.  **Dependencies**:
    ```bash
    pip install requests google-genai python-dotenv
    ```
2.  **Configure**: Add your `GEMINI_API_KEY` to a `.env` file.
3.  **Launch**:
    ```bash
    python chat.py
    ```

---

## 🏗️ Universal Deployment

TRC is built for the "Always-On" edge.
- **Docker**: Deploy a team command center in seconds. See [deployment.md](deployment.md).
- **Raspberry Pi**: Use `scripts/setup_pi.sh` to register TRC as a 24/7 background `systemd` service.

---

## ⌨️ Command Suite

| Category | Commands |
|:---|:---|
| **Intelligence** | `/trc`, `/whisper`, `/analyze`, `/pulse` |
| **Coordination**| `/topic`, `/nick`, `/who`, `/broadcast` |
| **Navigation**  | `/join`, `/leave`, `/switch`, `/history` |
| **Diagnostic**  | `/logs`, `/wipe`, `/clear`, `/logout` |

---
*Built for the Gemini 3 Hackathon. Transforming simple transmission into intelligent orchestration.* 🎬🦾✨
