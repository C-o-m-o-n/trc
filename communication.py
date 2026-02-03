## communication.py module
## receive messages and send messages
## threading with ability to start thread using a function callback

import time
import json
import requests
import threading
from urllib.parse import quote
from requests.exceptions import RequestException
from datetime import datetime

publishKey = 'demo'
subscribeKey = 'demo'

# flag to help with graceful shutdown
running = True

# Track active streams per channel
active_streams = {}

# Internal diagnostic logs
logs = []

def add_log(event: str, level: str = "INFO"):
    """Add a diagnostic event to the log buffer"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    logs.append(f"[{timestamp}] {level}: {event}")
    # Keep last 50 logs to prevent memory leak
    if len(logs) > 50:
        logs.pop(0)

def get_logs(count: int = 20):
    """Return the latest logs"""
    return logs[-count:]

def clear_logs():
    """Clear all diagnostic logs"""
    logs.clear()

## update running flag
def update_running(value: bool):
    global running
    running = value

## Connect To a Channel
def stream(channel: str, callback):
    tt = '0'
    fail_count = 0
    was_failing = False
    while running and channel in active_streams:
        receive_url = f'https://ps.pndsn.com/subscribe/{subscribeKey}/{channel}/0/{tt}'
        try:
            response = requests.get(receive_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            tt = data[1]
            
            if was_failing:
                add_log(f"Connection restored for #{channel}", "SUCCESS")
                print(f"\n[+] Connection restored in #{channel}!")
                was_failing = False
            
            fail_count = 0 # Reset on success
            # Pass channel info along with data
            callback(channel, data)
        except RequestException as e:
            fail_count += 1
            was_failing = True
            
            # Log detailed technical info
            add_log(f"Stream failure in #{channel}: {str(e)}", "ERROR")
            
            # Only alert the user after multiple consecutive failures
            if fail_count == 5:
                print(f"\n[!] Connection lost in #{channel}. Retrying in background...")
            elif fail_count > 5 and fail_count % 30 == 0:
                # Every ~1 minute (30 * 2s)
                print(f"[!] Still attempting to reconnect to #{channel} (DNS/Network issue)...")
            
            time.sleep(2) # Back off to wait for network recovery
            continue
        except Exception as e:
            add_log(f"Unexpected error in #{channel}: {str(e)}", "CRITICAL")
            print(f"\n[UNEXPECTED ERROR] #{channel} stream: {e}")
            break
        finally:
            time.sleep(0.1)

def startStream(channel: str, callback):
    """Start a stream for a channel"""
    if channel in active_streams:
        return active_streams[channel]  # Already streaming
    
    thread = threading.Thread(
        target=stream,
        args=(channel, callback)
    )
    # Add to active_streams BEFORE starting thread (fixes race condition)
    active_streams[channel] = thread
    thread.daemon = True # Ensure thread dies with main process
    thread.start()
    return thread

def stopStream(channel: str):
    """Stop streaming a specific channel"""
    if channel in active_streams:
        del active_streams[channel]
        return True
    return False

def getActiveChannels():
    """Return list of active channels"""
    return list(active_streams.keys())

def send(channel: str, payload: dict):
    """Send a message and return status dict"""
    encoded_payload = quote(json.dumps(payload), safe='')
    send_url = f'https://ps.pndsn.com/publish/{publishKey}/{subscribeKey}/0/{channel}/0/{encoded_payload}'
    try:
        response = requests.get(send_url, timeout=5)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 403:
            add_log(f"Send failed (403): Check API keys", "ERROR")
            return {"success": False, "error": "Forbidden: Check your API keys", "code": 403}
        elif response.status_code == 429:
            add_log(f"Send failed (429): Rate limited", "WARNING")
            return {"success": False, "error": "Rate limited: Slow down!", "code": 429}
        else:
            add_log(f"Send failed ({response.status_code})", "ERROR")
            return {"success": False, "error": f"HTTP Error {response.status_code}", "code": response.status_code}
            
    except RequestException as e:
        add_log(f"Send network error: {str(e)}", "ERROR")
        return {"success": False, "error": f"Network Error: {type(e).__name__}", "code": 0}
    except Exception as e:
        add_log(f"Send unexpected error: {str(e)}", "CRITICAL")
        return {"success": False, "error": f"Unexpected Error: {str(e)}", "code": -1}

def getHistory(channel: str, count: int = 10):
    """Fetch recent messages and return status dict"""
    history_url = f'https://ps.pndsn.com/v2/history/sub-key/{subscribeKey}/channel/{channel}?count={count}'
    try:
        response = requests.get(history_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Messages are in data[0]
            messages = data[0] if data else []
            return {"success": True, "data": messages}
        else:
            add_log(f"History fetch failed ({response.status_code})", "ERROR")
            return {"success": False, "error": f"HTTP Error {response.status_code}", "code": response.status_code}
            
    except RequestException as e:
        add_log(f"History network error: {str(e)}", "ERROR")
        return {"success": False, "error": f"Network Error: {type(e).__name__}", "code": 0}
    except Exception as e:
        add_log(f"History unexpected error: {str(e)}", "CRITICAL")
        return {"success": False, "error": f"Unexpected Error: {str(e)}", "code": -1}
        
## Test for the module
if __name__ == '__main__':
    channel = 'chat'
    startStream(channel, callback=lambda ch, m: print(f"{ch}: {m}"))
    while True:
        status = send(channel, {"user": "tester", "message": "hello!!!"})
        print(f"Send status: {status}")
        time.sleep(1)
