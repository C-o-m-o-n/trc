# Strategic Comparison: TRC vs. IRC 📡⚔️

At a glance, TRC looks like a simple TUI chat similar to IRC (Internet Relay Chat). However, for the **Gemini 3 Hackathon**, the distinction is critical. TRC is not just a chat client; it is an **Intelligence Layer**.

| Feature | IRC (Internet Relay Chat) | TRC (Terminal Relay Controller) |
| :--- | :--- | :--- |
| **Core Role** | Messaging Protocol | Intelligence Orchestrator |
| **Connectivity** | Client-Server (TCP/7000) | Edge-Native (Pub/Sub) |
| **Persistence** | None (Requires BNC/Logs) | Native SQLite Persistence |
| **Intelligence** | External Bots (Procedural) | Embedded Brain (Agentic) |
| **Context** | Single-channel focus | Multi-channel technical reasoning |

## 1. The "Relay" vs. "Chat" Distinction
In IRC, you join a channel to talk. In TRC, you join a channel to **monitor**. 
TRC's primary value isn't the typing; it's the **Relay Logic**. Gemini 2.5 Flash sits at the center, watching multiple streams (Relays) and synthesising them into a single "Technical Pulse."

## 2. native AI Orchestration
Standard IRC bots are **Procedural** (If `!help` then `print help`). 
TRC's Orchestrator is **Agentic**. It has access to:
-   **Channel History**: (SQLite Querying)
-   **File System**: (Code Inspection)
-   **Vision**: (Multimodal Diagnosis)

## 3. The "Edge-Native" Advantage
IRC was built for the 1980s internet. TRC is built for the **24/7 Intelligent Listener** era. 
TRC is optimized to run headless on a Raspberry Pi or an SRE terminal, acting as a "Proactive Guardian" that pings you only when it identifies a cross-channel anomaly (e.g., a commit in `#git` followed by a spike in `#latency`).

## Summary for Judges
IRC is about **Transmission**. 
TRC is about **Observation and Action**. 
We aren't building a "Messenger"; we are building a **Mission Control for Distributed Teams**.
