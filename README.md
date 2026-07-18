# TRC (Terminal Relay Controller) 🛰️🧠🏗️

**"Beyond Chat: Intelligent Mission Control for Technical Teams"**

TRC is an AI-orchestrated communication middleware designed for DevOps, SRE, and Edge engineering teams. Built with Python and PubNub, TRC transforms raw technical relays into a **Mission Control Center** where Gemini 2.5 Flash acts as an active technical guardian and project manager.

---

## ✨ Orchestrated Features

### 🧠 The Intelligence Layer (Gemini 2.5 Flash)
- **Tool-Augmented Orchestration**: Gemini has "hands" to read local code and query technical history autonomously. Any proposed file write is shown as a diff and requires your explicit `y/n` confirmation before it's applied.
- **Proactive Monitor Mode**: Passively watches background relays and triggers **Autonomous Technical Alerts** if crashes or blockers are detected.
- **Vision Engine**: Analyze screenshots of errors directly in the terminal via `/analyze`.
- **Pulse Reports**: Cross-channel technical health summaries via `/pulse`.

### 📡 IRC Parity (Professional Coordination)
- **AI-Aware Topics**: `/topic` sets a mission context that informs Gemini's technical reasoning.
- **Persistent Identity**: Secure your handle with `/nick`, saved to a local SQLite settings table.
- **Private Consulting**: `/whisper` for one-on-one technical brainstorming with the AI Brain.
- **Participant Roster**: See everyone known to have posted in the relay with `/who` (all-time, not a live presence check).

---

## 🏗️ Architecture: The Intelligence Loop
TRC doesn't just sync messages; it creates a feedback loop between the network and the machine.
- **Listen**: PubNub Real-time Network.
- **Remember**: Local SQLite Persistence.
- **Reason**: Gemini 2.5 Flash Reasoning Engine.
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
    - Optionally set `PUBLISH_KEY`/`SUBSCRIBE_KEY` (see the warning below) and `TRC_DB_PATH` (local SQLite history file location) — see `.env.example`.
    - Install standard requirements: `pip install -r requirements.txt`
3.  **Launch Your Engine**:
    ```bash
    python chat.py
    ```

---

## 🧪 Development

Automated tests cover `database.py` (SQLite persistence, dedup, upserts). To run them:
```bash
pip install -r requirements-dev.txt
pytest
```

---

## 🏗️ How People Use TRC (The User Journey)

TRC isn't just a site you visit; it's a **Technical Controller** you deploy.

### 1. The Commander (Initiator)
A lead engineer clones the repo and starts a relay for a specific technical mission (e.g., `#incident-402`). They set the `/topic` and provide the AI with initial context.

### 2. The Team (Participants)
Other engineers clone the repo, use the same PubNub keys (set via `PUBLISH_KEY`/`SUBSCRIBE_KEY` in `.env` — defaults to PubNub's public `demo` keyspace if unset), and join the relay. They instantly get the benefits of the "Shared Brain" that has been watching the technical stream.

> [!WARNING]
> The default `demo` PubNub keyspace is public - anyone else using the demo keys can read and write to a channel with the same name. Set real `PUBLISH_KEY`/`SUBSCRIBE_KEY` values in `.env` for anything beyond local testing.

### 3. The Edge Guard (Always-On)
The team deploys a **Headless TRC** instance on a Raspberry Pi (using `scripts/setup_pi.sh`) that stays in the channel 24/7, even when humans log off, to provide proactive anomaly detection.

---


## ⌨️ Command Suite (v1.2.0)

| Category | Command | Description |
| :--- | :--- | :--- |
| **Messaging** | `/join #channel` | Join and switch to a technical relay |
| | `/leave #channel` | Gracefully leave a relay |
| | `/switch #channel` | Change active focus without leaving |
| | `/broadcast [text]`| Syndicate a message to ALL joined relays |
| | `/channels` | List all joined relays |
| **Intelligence** | `/trc [query]` | Context-aware reasoning (Gemini-aware) |
| | `/whisper [text]` | Private technical consultation with the AI |
| | `/topic [text]` | Set mission objective (sets AI context) |
| | `/analyze` | Multimodal terminal screenshot diagnosis |
| | `/nick [name]` | Change persistent technical identity |
| | `/who` | List all known relay participants (all-time, not live presence) |
| **Utilities** | `/history [N\|local]`| Remote or Local SQLite technical history |
| | `/logs [N]` | View background diagnostic logs |
| | `/wipe` | Clear local history for the current channel |
| | `/clear` | Purge terminal screen |
| | `/logout` | Graceful Mission Control shutdown |


---
*Built for the Gemini 3 Hackathon. Transforming simple transmission into intelligent orchestration.* 🎬🦾✨
