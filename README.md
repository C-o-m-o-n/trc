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

## 🚀 Quick Start (Team Setup)

TRC is distributed as a technical codebase. To get started:

1.  **Clone the Mission Control**:
    ```bash
    git clone https://github.com/C-o-m-o-n/trc.git
    cd trc
    ```
2.  **Environment Setup**:
    - Create a `.env` file and add your `GEMINI_API_KEY`.
    - Install standard requirements: `pip install requests google-genai python-dotenv`
3.  **Launch Your Engine**:
    ```bash
    python chat.py
    ```

---

## 🏗️ How People Use TRC (The User Journey)

TRC isn't just a site you visit; it's a **Technical Controller** you deploy.

### 1. The Commander (Initiator)
A lead engineer clones the repo and starts a relay for a specific technical mission (e.g., `#incident-402`). They set the `/topic` and provide the AI with initial context.

### 2. The Team (Participants)
Other engineers clone the repo, use the same PubNub keys (configured in `communication.py`), and join the relay. They instantly get the benefits of the "Shared Brain" that has been watching the technical stream.

### 3. The Edge Guard (Always-On)
The team deploys a **Headless TRC** instance on a Raspberry Pi (using `scripts/setup_pi.sh`) that stays in the channel 24/7, even when humans log off, to provide proactive anomaly detection.

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
