## chat.py
## Simple chat client with multi-channel support and error handling
import communication
import threading
import time
import os
import database
import ai_engine
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

def show_local_history(channel, count=50):
    """Display messages stored in the local SQLite database"""
    print(f"\n{GREEN}--- Local History for #{channel} (Last {count}) ---{RESET}")
    history = database.get_local_history(channel, count)
    
    if history:
        for msg in history:
            user = msg.get("user", "Unknown")
            text = msg.get("message", "")
            time_str = msg.get("timestamp", "--:--")
            
            if "SYSTEM" in user:
                print(f"{YELLOW}[{time_str}] ⚡ {text}{RESET}")
            else:
                print(f"{CYAN}[{time_str}] ← [{user}]: {text}{RESET}")
    else:
        print(f"{CYAN}No local history found for this channel.{RESET}")
        
    print(f"{GREEN}--- End of Local History ---{RESET}\n")

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
    input(f"{YELLOW}Press Enter to continue...{RESET}")

def show_help():
    """Show the help menu"""
    print(f"\n{BOLD}{CYAN}TRC Command Suite - v1.1.0{RESET}")
    print(f"{YELLOW}--- Messaging ---{RESET}")
    print(f"  /join #channel       Join and switch to a channel")
    print(f"  /leave #channel      Leave a channel")
    print(f"  /switch #channel     Switch active focus")
    print(f"  /broadcast [text]    Send message to ALL joined channels")
    print(f"{YELLOW}--- AI Orchestration ---{RESET}")
    print(f"  /trc [query]         Ask Gemini about current channel history")
    print(f"  /whisper [text]      Private brainstorm with Gemini (not relayed)")
    print(f"  /analyze [path]      Send an image/screenshot for AI diagnosis")
    print(f"  /pulse               Cross-channel technical health report")
    print(f"{YELLOW}--- IRC & Context ---{RESET}")
    print(f"  /topic [text]        Set/View channel objective (Gemini-aware)")
    print(f"  /nick [name]         Change your identity (saved to DB)")
    print(f"  /who                 List active technical participants")
    print(f"{YELLOW}--- Utilities ---{RESET}")
    print(f"  /history [N|local]   Show remote or local SQLite history")
    print(f"  /logs [N]            View technical diagnostic logs")
    print(f"  /wipe                Clear local history for current channel")
    print(f"  /clear               Clear terminal screen")
    print(f"  /logout              Graceful exit")
    print(f"\n{MAGENTA}📡 [Monitor Mode]: TRC is passively watching background relays.{RESET}")
    print(f"{MAGENTA}   Gemini will ALERT you if technical anomalies are detected.{RESET}\n")
    input(f"{YELLOW}Press Enter to continue...{RESET}")

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
    global current_channel, current_user
    # Remove # if present
    channel_name = channel_name.lstrip('#')
    
    if not channel_name:
        print(f"{RED}Usage: /join #channel_name{RESET}")
        return
    
    channels = communication.getActiveChannels()
    if channel_name in channels:
        print(f"{YELLOW}Already in #{channel_name}{RESET}")
        return
    
    communication.startStream(channel_name, on_message_received, on_anomaly_detected)
    
    join_msg = {"user": "SYSTEM", "message": f"{current_user} has joined"}
    status = communication.send(channel_name, join_msg)
    
    if status["success"]:
        current_channel = channel_name
        print(f"{GREEN}Joined #{channel_name} and switched to it{RESET}")
        print(f"{MAGENTA}📡 [Monitor Mode]: Proactive AI watcher enabled for #{channel_name}{RESET}")
    else:
        print(f"{RED}❌ Error joining #{channel_name}: {status['error']}{RESET}")

def leave_channel(channel_name):
    """Leave a channel"""
    global current_channel, current_user
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
    global current_user, current_channel
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
        if not args:
             show_history(current_channel, 10)
             return
        
        if args[0].lower() == "local":
            count = 50
            if len(args) > 1:
                try: count = int(args[1])
                except ValueError: pass
            show_local_history(current_channel, count)
            return
             
        try:
            count = int(args[0])
            if count <= 0:
                print(f"{RED}❌ Please enter a positive number for history.{RESET}")
                return
            show_history(current_channel, count)
        except ValueError:
            print(f"{RED}❌ Invalid argument: '{args[0]}'. Usage: /history [N|local]{RESET}")
    
    elif cmd == "pulse":
        print(f"\n{MAGENTA}🛸 [TRC Pulse] Gemini is reasoning over channel history...{RESET}")
        # Fetch history for ALL joined channels
        channels = communication.getActiveChannels()
        multi_history = {}
        for ch in channels:
            multi_history[ch] = database.get_local_history(ch, limit=30)
        
        report = ai_engine.ai_engine.get_pulse(multi_history)
        print(f"\n{YELLOW}╔══════════ AI PULSE REPORT ══════════╗{RESET}")
        print(f"{report}")
        print(f"{YELLOW}╚═════════════════════════════════════╝{RESET}\n")
        input(f"{YELLOW}Press Enter to continue...{RESET}")

    elif cmd == "trc":
        if not args:
            print(f"{RED}Usage: /trc your question about the current channel{RESET}")
            return
        
        question = " ".join(args)
        print(f"\n{MAGENTA}🧠 [TRC Brain] Asking Gemini for context...{RESET}")
        context = database.get_local_history(current_channel, limit=30)
        answer = ai_engine.ai_engine.generate_response(question, current_channel, context)
        print(f"\n{CYAN}🤖 [Gemini]: {answer}{RESET}\n")
        input(f"{YELLOW}Press Enter to continue...{RESET}")

    elif cmd == "analyze":
        if not args:
            print(f"{RED}Usage: /analyze [path_to_image]{RESET}")
            return
        
        path = args[0]
        prompt = " ".join(args[1:]) if len(args) > 1 else None
        
        print(f"\n{MAGENTA}👁️ [Vision Engine] Gemini is analyzing the image...{RESET}")
        report = ai_engine.ai_engine.analyze_image(path, prompt)
        
        print(f"\n{YELLOW}╔══════════ VISION REPORT ══════════╗{RESET}")
        print(f"{report}")
        print(f"{YELLOW}╚═══════════════════════════════════╝{RESET}\n")
        input(f"{YELLOW}Press Enter to continue...{RESET}")

    elif cmd == "wipe":
        confirm = input(f"{RED}Are you sure you want to wipe local history for #{current_channel}? (y/n): {RESET}").lower()
        if confirm == 'y':
            if database.clear_channel_history(current_channel):
                print(f"{GREEN}Local history for #{current_channel} has been wiped.{RESET}")
            else:
                print(f"{RED}Failed to clear local history.{RESET}")
        else:
            print(f"{YELLOW}Wipe cancelled.{RESET}")

    elif cmd == "logs":
        count = 20
        if args:
            try:
                count = int(args[0])
            except ValueError:
                pass
        show_logs(count)
    
    elif cmd == "topic":
        if not args:
            topic = database.get_channel_topic(current_channel)
            if topic:
                print(f"{YELLOW}#{current_channel} TOPIC: {topic}{RESET}")
            else:
                print(f"{YELLOW}No topic set for #{current_channel}. Use /topic [text] to set one.{RESET}")
        else:
            new_topic = " ".join(args)
            database.set_channel_topic(current_channel, new_topic)
            print(f"{GREEN}Topic updated! Gemini is now aware of this objective.{RESET}")
            # Announce to channel
            topic_msg = {"user": "SYSTEM", "message": f"{current_user} changed the topic to: {new_topic}"}
            communication.send(current_channel, topic_msg)

    elif cmd == "nick":
        if not args:
            print(f"{RED}Usage: /nick new_name{RESET}")
            return
        new_nick = args[0]
        # Same checks as startup
        if new_nick.upper() in ["SYSTEM", "ADMIN", "ROOT", "SERVER", "MODERATOR"]:
             print(f"{RED}❌ Reserved name.{RESET}")
             return
        
        old_nick = current_user
        current_user = new_nick
        database.update_setting("nick", new_nick)
        print(f"{GREEN}Your nickname is now {current_user}{RESET}")
        # Announce to current channel
        nick_msg = {"user": "SYSTEM", "message": f"{old_nick} is now known as {new_nick}"}
        communication.send(current_channel, nick_msg)

    elif cmd == "whisper":
        if not args:
            print(f"{RED}Usage: /whisper [your private message to Gemini]{RESET}")
            return
        question = " ".join(args)
        print(f"\n{MAGENTA}🤫 [Whisper] Consulting Gemini privately...{RESET}")
        # Direct response without public relay
        answer = ai_engine.ai_engine.generate_response(question, current_channel)
        print(f"\n{CYAN}🤖 [Gemini]: {answer}{RESET}\n")

    elif cmd == "who":
        users = database.get_active_users(current_channel)
        print(f"\n{YELLOW}Active in #{current_channel}:{RESET}")
        if not users:
            print(f"  {CYAN}No history of other users yet.{RESET}")
        else:
            for u in users:
                prefix = f"{GREEN}●{RESET}" if u == current_user else f"{CYAN}○{RESET}"
                print(f"  {prefix} {u}")
        print()
    
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

def on_anomaly_detected(channel, messages):
    """Callback when the background AI watcher detects a technical anomaly"""
    report = ai_engine.ai_engine.detect_anomalies(messages, channel)
    if report:
        display_alert(channel, report)

def display_alert(channel, report):
    """Display a high-visibility AI alert in the terminal"""
    print(f"\n\n{RED}{BOLD}╔═══════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}{BOLD}║         ⚠️  AUTONOMOUS TECHNICAL ALERT            ║{RESET}")
    print(f"{RED}{BOLD}╠═══════════════════════════════════════════════════╣{RESET}")
    print(f"{YELLOW}  SOURCE: #{channel}{RESET}")
    print(f"{WHITE}  {report.replace('ALERT:', '').strip()}{RESET}")
    print(f"{RED}{BOLD}╚═══════════════════════════════════════════════════╝{RESET}\n")
    # Trigger a small bell sound if terminal supports it
    print('\a', end='')

# === MAIN PROGRAM ===

# Check for CLI overrides
cli_nick = None
if "--nick" in sys.argv:
    idx = sys.argv.index("--nick")
    if idx + 1 < len(sys.argv):
        cli_nick = sys.argv[idx + 1]

# Welcome and handle identity
print(f"{BOLD}{GREEN}Welcome to Chat!{RESET}")

# 1. Handle CLI Override
if cli_nick:
    current_user = cli_nick
    print(f"{MAGENTA}🎭 CLI Override: Identified as {BOLD}{current_user}{RESET}")
# 2. Standard initialization
else:
    saved_nick = database.get_setting("nick")
    if saved_nick:
        ans = input(f"Continue as {BOLD}{saved_nick}{RESET}? (Y/n): ").strip().lower()
        if ans == '' or ans == 'y':
            current_user = saved_nick
            print(f"{GREEN}Welcome back, {BOLD}{current_user}{RESET}!")
        else:
            saved_nick = None # Reset to trigger new name input

    if not saved_nick:
        while True:
            user_input = input(f"{BLUE}Username: {YELLOW}").strip()
            
            # 1. Check if empty
            if not user_input:
                print(f"{RED}❌ Username cannot be empty.{RESET}")
                continue
                
            # 2. Check for reserved names (spoof prevention)
            reserved = ["SYSTEM", "ADMIN", "ROOT", "SERVER", "MODERATOR"]
            if user_input.upper() in reserved:
                print(f"{RED}❌ '{user_input}' is a reserved system name. Please choose another.{RESET}")
                continue
                
            # 3. Check for invalid characters
            if "\n" in user_input or "\r" in user_input or "\t" in user_input:
                print(f"{RED}❌ Username contains invalid characters.{RESET}")
                continue
                
            # All checks passed
            current_user = user_input
            database.update_setting("nick", current_user)
            break

print(f"{GREEN}Joined as {current_user}. Type /help for commands.{RESET}")
print(f"{CYAN}Starting in #{current_channel}{RESET}\n")

# Start listening on default channel
communication.startStream(current_channel, on_message_received, on_anomaly_detected)

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
    
    # Check for excessive length
    if len(message) > 1000:
        print(f"{RED}❌ Message too long! ({len(message)}/1000 characters). Please shorten it.{RESET}")
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
