## chat.py
## Simple chat client with multi-channel support and error handling
import communication
import sys
from datetime import datetime

# Colors for terminal
BOLD = '\033[1m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RED = '\033[31m'
CYAN = '\033[36m'
MAGENTA = '\033[35m'
RESET = '\033[0m'

# Store the current username and active channel
current_user = ""
current_channel = "general"

def format_time():
    """Return current time as HH:MM"""
    return datetime.now().strftime("%H:%M")

def show_history(channel, count=10):
    """Display message history for a channel"""
    print(f"\n{YELLOW}--- Last {count} messages in #{channel} ---{RESET}")
    result = communication.getHistory(channel, count)
    
    if result["success"]:
        history = result["data"]
        if history:
            for msg in history:
                if isinstance(msg, dict):
                    user = msg.get("user", "Unknown")
                    text = msg.get("message", "")
                    if "SYSTEM" in user:
                        print(f"{YELLOW}⚡ {text}{RESET}")
                    else:
                        print(f"{CYAN}← [{user}]: {text}{RESET}")
        else:
            print(f"{CYAN}No message history yet.{RESET}")
    else:
        print(f"{RED}❌ Could not fetch history: {result['error']}{RESET}")
        
    print(f"{YELLOW}--- End of History ---{RESET}\n")

def show_logs(count=20):
    """Display internal technical logs"""
    print(f"\n{RED}--- Technical Diagnostic Logs (Last {count}) ---{RESET}")
    logs = communication.get_logs(count)
    if logs:
        for log in logs:
            if "ERROR" in log or "CRITICAL" in log:
                print(f"{RED}{log}{RESET}")
            elif "SUCCESS" in log:
                print(f"{GREEN}{log}{RESET}")
            else:
                print(f"{YELLOW}{log}{RESET}")
    else:
        print(f"{CYAN}No diagnostic logs captured yet.{RESET}")
    print(f"{RED}--- End of Logs ---{RESET}\n")

def show_help():
    """Display available commands"""
    print(f"""
{YELLOW}╔══════════════════════════════════════════╗
║            Available Commands            ║
╠══════════════════════════════════════════╣
║  {CYAN}/help{YELLOW}         - Show this help          ║
║  {CYAN}/channels{YELLOW}     - List joined channels   ║
║  {CYAN}/join #name{YELLOW}   - Join a channel         ║
║  {CYAN}/leave #name{YELLOW}  - Leave a channel        ║
║  {CYAN}/switch #name{YELLOW} - Switch active channel  ║
║  {CYAN}/broadcast{YELLOW}    - Send to ALL channels   ║
║  {CYAN}/history{YELLOW}      - Show last 10 messages  ║
║  {CYAN}/history N{YELLOW}    - Show last N messages   ║
║  {CYAN}/logs{YELLOW}         - Show technical logs    ║
║  {CYAN}/clear{YELLOW}        - Clear the screen       ║
║  {CYAN}/logout{YELLOW}       - Leave the chat         ║
╚══════════════════════════════════════════╝{RESET}
""")

def show_channels():
    """Display list of joined channels"""
    channels = communication.getActiveChannels()
    print(f"\n{YELLOW}Joined channels:{RESET}")
    for ch in channels:
        if ch == current_channel:
            print(f"  {GREEN}● #{ch} (active){RESET}")
        else:
            print(f"  {CYAN}○ #{ch}{RESET}")
    print()

def clear_screen():
    """Clear the terminal screen"""
    print('\033[2J\033[H', end='')

def join_channel(channel_name):
    """Join a new channel"""
    global current_channel
    # Remove # if present
    channel_name = channel_name.lstrip('#')
    
    if not channel_name:
        print(f"{RED}Usage: /join #channel_name{RESET}")
        return
    
    channels = communication.getActiveChannels()
    if channel_name in channels:
        print(f"{YELLOW}Already in #{channel_name}{RESET}")
        return
    
    communication.startStream(channel_name, on_message_received)
    join_msg = {"user": "SYSTEM", "message": f"{current_user} has joined"}
    status = communication.send(channel_name, join_msg)
    
    if status["success"]:
        current_channel = channel_name
        print(f"{GREEN}Joined #{channel_name} and switched to it{RESET}")
    else:
        print(f"{RED}❌ Error joining #{channel_name}: {status['error']}{RESET}")

def leave_channel(channel_name):
    """Leave a channel"""
    global current_channel
    channel_name = channel_name.lstrip('#')
    
    if not channel_name:
        print(f"{RED}Usage: /leave #channel_name{RESET}")
        return
    
    channels = communication.getActiveChannels()
    if channel_name not in channels:
        print(f"{RED}Not in #{channel_name}{RESET}")
        return
    
    if len(channels) == 1:
        print(f"{RED}Can't leave your only channel! Join another first.{RESET}")
        return
    
    leave_msg = {"user": "SYSTEM", "message": f"{current_user} has left"}
    status = communication.send(channel_name, leave_msg)
    
    if status["success"]:
        communication.stopStream(channel_name)
        if current_channel == channel_name:
            current_channel = communication.getActiveChannels()[0]
            print(f"{YELLOW}Left #{channel_name}, switched to #{current_channel}{RESET}")
        else:
            print(f"{YELLOW}Left #{channel_name}{RESET}")
    else:
        print(f"{RED}❌ Error leaving #{channel_name}: {status['error']}{RESET}")

def switch_channel(channel_name):
    """Switch to a different channel"""
    global current_channel
    channel_name = channel_name.lstrip('#')
    
    if not channel_name:
        print(f"{RED}Usage: /switch #channel_name{RESET}")
        return
    
    channels = communication.getActiveChannels()
    if channel_name not in channels:
        print(f"{RED}Not in #{channel_name}. Join it first with /join #{channel_name}{RESET}")
        return
    
    current_channel = channel_name
    print(f"{GREEN}Switched to #{channel_name}{RESET}")

def handle_command(command):
    """Process a command"""
    parts = command[1:].split()
    cmd = parts[0].lower() if parts else ""
    args = parts[1:] if len(parts) > 1 else []
    
    if cmd == "help":
        show_help()
    
    elif cmd == "channels":
        show_channels()
    
    elif cmd == "join":
        join_channel(args[0] if args else "")
    
    elif cmd == "leave":
        leave_channel(args[0] if args else "")
    
    elif cmd == "switch":
        switch_channel(args[0] if args else "")
    
    elif cmd == "history":
        count = 10
        if args:
            try:
                count = int(args[0])
            except ValueError:
                print(f"{RED}Invalid number. Using default (10).{RESET}")
        show_history(current_channel, count)
    
    elif cmd == "logs":
        count = 20
        if args:
            try:
                count = int(args[0])
            except ValueError:
                pass
        show_logs(count)
    
    elif cmd == "clear":
        clear_screen()
    
    elif cmd == "broadcast":
        if not args:
            print(f"{RED}Usage: /broadcast your message here{RESET}")
            return
        broadcast_text = ' '.join(args)
        success_count = 0
        total_channels = 0
        for ch in communication.getActiveChannels():
            total_channels += 1
            payload = {"user": current_user, "message": broadcast_text, "broadcast": True}
            status = communication.send(ch, payload)
            if status["success"]:
                success_count += 1
        
        time_str = format_time()
        if success_count == total_channels:
            print(f"{MAGENTA}[{time_str}] 📢 Broadcast to {success_count} channels: {broadcast_text}{RESET}")
        else:
            print(f"{YELLOW}[{time_str}] 📢 Broadcast partially sent ({success_count}/{total_channels} channels).{RESET}")
    
    elif cmd == "logout":
        # Leave all channels gracefully
        for ch in communication.getActiveChannels():
            leave_msg = {"user": "SYSTEM", "message": f"{current_user} has left"}
            communication.send(ch, leave_msg)
        communication.update_running(False)
        print(f"{GREEN}Goodbye! 👋{RESET}")
        sys.exit()
    
    else:
        print(f"{RED}Unknown command: /{cmd}. Type /help for commands.{RESET}")

def on_message_received(channel, data):
    """Handle incoming messages from any channel"""
    for msg in data[0]:
        if not isinstance(msg, dict):
            continue
        
        user = msg.get("user", "")
        text = msg.get("message", "")
        is_broadcast = msg.get("broadcast", False)
        time_str = format_time()
        
        # Skip our own messages
        if user == current_user:
            continue
        
        # Only show messages from current channel (unless broadcast or system)
        if channel != current_channel and not is_broadcast and "SYSTEM" not in user:
            continue
        
        # Format based on message type
        if "SYSTEM" in user:
            print(f"\n{YELLOW}[{time_str}] ⚡ {text}{RESET}")
        elif is_broadcast:
            print(f"\n{MAGENTA}[{time_str}] 📢 [{user}]: {text}{RESET}")
        else:
            print(f"\n{CYAN}[{time_str}] ← [{user}]: {text}{RESET}")

# === MAIN PROGRAM ===

# Welcome and get username
print(f"{BOLD}{GREEN}Welcome to Chat!{RESET}")
current_user = input(f"{BLUE}Username: {YELLOW}").strip()

if not current_user:
    current_user = "Anonymous"

print(f"{GREEN}Joined as {current_user}. Type /help for commands.{RESET}")
print(f"{CYAN}Starting in #{current_channel}{RESET}\n")

# Start listening on default channel
communication.startStream(current_channel, on_message_received)

# Announce that we joined
join_msg = {"user": "SYSTEM", "message": f"{current_user} has joined"}
status = communication.send(current_channel, join_msg)
if not status["success"]:
    print(f"{RED}⚠️ Warning: Could not send join notification to #{current_channel} ({status['error']}){RESET}")

# Main loop
while True:
    message = input(f"{MAGENTA}#{current_channel} {BLUE}> {RESET}").strip()
    
    if not message:
        continue
    
    # Check if it's a command
    if message.startswith('/'):
        handle_command(message)
        continue
    
    # Send the message to current channel
    payload = {"user": current_user, "message": message}
    status = communication.send(current_channel, payload)
    
    time_str = format_time()
    if status["success"]:
        print(f"{GREEN}[{time_str}] → {message}{RESET}")
    else:
        print(f"{RED}❌ Failed to send: {status['error']}{RESET}")
