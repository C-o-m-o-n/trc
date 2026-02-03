# TRC Global Deployment Architecture 📡🌎

## 1. How it works
TRC is based on a **Decentralized Relay Architecture**. Unlike a traditional web app with one server, TRC uses a global Pub-Sub bus (PubNub) as the communication backbone.

### The Nodes:
-   **User Nodes**: Any laptop (Windows/Mac/Linux) running `chat.py`.
-   **Listen Nodes**: A Raspberry Pi or any low-power device running a "headless" version of the agent.
-   **Relay Service**: The PubNub cloud (handles the global discovery and delivery).

## 2. Accessibility for Judges & Friends
You asked: *"If we deploy it on my pi, will anyone else try out TRC?"*

**The Answer is YES.** 
Since the logic is in the cloud relay, anyone with the TRC code can join the same room.

| Device | Role | Use Case |
| :--- | :--- | :--- |
| **Your Raspberry Pi** | **Permanent Listener** | Acts as the "Team Memory" node. Stays online 24/7 to record every message into SQLite and provide AI summaries. |
| **A Judge's Laptop** | **Standard Client** | They run `python chat.py` and join `#general`. They instantly see you and can interact with the Gemini-powered agent running on your Pi. |
| **Your Friend's PC** | **Standard Client** | They join the same channel and participate in the relay. |

## 3. The "WOW" Factor for Deployment
We will offer two ways to use TRC:
1.  **The Live Demo Room**: A pre-configured channel where the judges can just run the script and immediately see our **Permanent AI Agent** (running on your Pi) already acting as the "Controller" of the room.
2.  **Private Relays**: They can spawn their own isolated relays for testing.

## 4. Deployment Readiness
-   **Code Portability**: The code is pure Python with minimal dependencies (`requests`, `sqlite3`). It runs anywhere.
-   **Zero Configuration**: We'll use "demo" keys or provide an easy `.env` setup so judges can start in 10 seconds.
