# TRC (Terminal Relay Chat) 🚀 📡

TRC is a high-performance, real-time terminal-based chat application powered by Python and PubNub. It supports multiple isolated channels, message history, and a robust command-driven interface.

## ✨ Features

- **Real-time Messaging**: Powered by PubNub's pub/sub architecture for near-instant message delivery.
- **Multi-Channel Support**: Join, leave, and switch between multiple rooms (e.g., `#general`, `#dev`, `#random`).
- **Command System**: Intuitive `/` commands for history, navigation, and system control.
- **Message History**: Fetch and view recent conversations instantly with `/history`.
- **Global Broadcast**: Send urgent announcements to all joined channels with `/broadcast`.
- **Graceful Shutdown**: Properly handles exits and notifies other users when you leave.
- **Visual UX**: Clean terminal interface with timestamps, directional indicators (→/←), and color-coded system alerts.
- **Smart Filtering**: Automatically hides your own echo from the backend for a cleaner feed.
- **Isolated Channels**: Chat in private rooms without overlapping conversations unless broadcasting.
- **TRC Powered**: Built on a modular networking core for reliability and speed.

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install requests
   ```

2. **Configure API Keys**:
   Currently, TRC uses `demo` keys for testing. For production, update the `publishKey` and `subscribeKey` in `communication.py`.

3. **Run the App**:
   ```bash
   python chat.py
   ```

## ⌨️ Commands

| Command | Description |
|:---|:---|
| `/help` | Show this help message with all available commands. |
| `/channels` | List all channels you are currently participating in. |
| `/join #name` | Join a new channel and switch to it. |
| `/leave #name` | Leave a specific channel. |
| `/switch #name` | Change your active channel without leaving others. |
| `/broadcast [msg]` | Send a message to every channel you have joined. |
| `/history [N]` | Display the last N messages from the current channel. |
| `/logs [N]` | Display the last N technical diagnostic logs. |
| `/clear` | Clear the terminal screen. |
| `/logout` | Gracefully exit the application and notify all channels. |

## 🏗️ Architecture

- **`chat.py`**: The main interface loop. Handles user input, command parsing, and message display.
- **`communication.py`**: The networking engine. Manages background threads for multiple channel streams and handles URL-encoded REST requests to PubNub.

---
*Built with ❤️ and Python.*
