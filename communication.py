## communication.py module
## receive messages and send messages over the PubNub relay network
## using the official pubnub SDK (real-time subscribe listener + sync publish/history calls)

import os
import json
import threading
from datetime import datetime

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNReconnectionPolicy
from pubnub.exceptions import PubNubException

import database

publishKey = os.getenv("PUBLISH_KEY", "demo")
subscribeKey = os.getenv("SUBSCRIBE_KEY", "demo")

# Constraints
MAX_MSG_LEN = 2000 # Backend limit higher than UI to allow for formatting

# flag to help with graceful shutdown
running = True

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
    if not value:
        pubnub.stop()

# Per-channel registered callbacks, guarded by _lock since the SDK delivers
# messages on its own background threads
_channel_callbacks = {}   # channel -> callback(channel, data)
_channel_watchers = {}    # channel -> watcher_callback(channel, messages)
_accumulators = {}        # channel -> accumulated messages for anomaly detection
ACCUMULATOR_LIMIT = 5      # Analyze every 5 messages
_lock = threading.Lock()

pnconfig = PNConfiguration()
pnconfig.publish_key = publishKey
pnconfig.subscribe_key = subscribeKey
pnconfig.uuid = f"trc-{os.getpid()}-{id(threading.current_thread())}"
pnconfig.ssl = True
pnconfig.reconnect_policy = PNReconnectionPolicy.EXPONENTIAL
pnconfig.daemon = True # Background subscribe threads die with the main process


class _TRCListener(SubscribeCallback):
    """Dispatches PubNub events to the channel-specific callbacks registered via startStream"""

    def message(self, pn, message_result):
        channel = message_result.channel
        payload = message_result.message
        if not isinstance(payload, dict):
            return

        user = payload.get("user", "Unknown")
        text = payload.get("message", "")

        # Real, globally-unique PubNub timetoken - reliable dedup key across reconnects
        database.save_message(
            channel=channel,
            user=user,
            message=text,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            timetoken=str(message_result.timetoken)
        )

        with _lock:
            callback = _channel_callbacks.get(channel)
            watcher_callback = _channel_watchers.get(channel)

        if callback:
            # Preserve the historical `data[0]` = list-of-messages shape callers expect
            callback(channel, [[payload], str(message_result.timetoken)])

        if watcher_callback and user != "SYSTEM":
            batch = None
            with _lock:
                acc = _accumulators.setdefault(channel, [])
                acc.append({"user": user, "message": text})
                if len(acc) >= ACCUMULATOR_LIMIT:
                    batch = list(acc)
                    acc.clear()
            if batch:
                watcher_callback(channel, batch)

    def status(self, pn, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            add_log("Connected to PubNub relay network", "SUCCESS")
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            add_log("Reconnected to PubNub relay network", "SUCCESS")
            print("\n[+] Connection restored!")
        elif status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            add_log("Unexpected disconnect from PubNub relay network", "ERROR")
            print("\n[!] Connection lost. Retrying in background...")
        elif status.category == PNStatusCategory.PNAccessDeniedCategory:
            add_log("Access denied: check your PUBLISH_KEY/SUBSCRIBE_KEY", "ERROR")
        elif status.is_error():
            add_log(f"Subscribe status error: {status.category}", "ERROR")

    def presence(self, pn, presence):
        pass


pubnub = PubNub(pnconfig)
pubnub.add_listener(_TRCListener())


def startStream(channel: str, callback, watcher_callback=None):
    """Start receiving messages for a channel with an optional AI watcher"""
    with _lock:
        already_active = channel in _channel_callbacks
        _channel_callbacks[channel] = callback
        _channel_watchers[channel] = watcher_callback
        _accumulators.setdefault(channel, [])

    if already_active:
        return

    pubnub.subscribe().channels([channel]).execute()


def stopStream(channel: str):
    """Stop streaming a specific channel"""
    with _lock:
        if channel not in _channel_callbacks:
            return False
        del _channel_callbacks[channel]
        _channel_watchers.pop(channel, None)
        _accumulators.pop(channel, None)

    pubnub.unsubscribe().channels([channel]).execute()
    return True


def getActiveChannels():
    """Return list of active channels"""
    with _lock:
        return list(_channel_callbacks.keys())


def send(channel: str, payload: dict):
    """Send a message and return status dict"""
    json_data = json.dumps(payload)

    # Basic length validation fallback
    if len(json_data) > MAX_MSG_LEN:
        add_log(f"Send rejected: Payload too large ({len(json_data)} characters)", "WARNING")
        return {"success": False, "error": f"Payload too large (Max {MAX_MSG_LEN})", "code": 413}

    try:
        envelope = pubnub.publish().channel(channel).message(payload).sync()
        return {"success": True, "data": envelope.result.timetoken}
    except PubNubException as e:
        add_log(f"Send failed: {str(e)}", "ERROR")
        return {"success": False, "error": str(e), "code": 0}
    except Exception as e:
        add_log(f"Send unexpected error: {str(e)}", "CRITICAL")
        return {"success": False, "error": f"Unexpected Error: {str(e)}", "code": -1}


def getHistory(channel: str, count: int = 10):
    """Fetch recent messages and return status dict"""
    try:
        envelope = pubnub.history().channel(channel).count(count).sync()
        messages = [item.entry for item in envelope.result.messages]
        return {"success": True, "data": messages}
    except PubNubException as e:
        add_log(f"History fetch failed: {str(e)}", "ERROR")
        return {"success": False, "error": str(e), "code": 0}
    except Exception as e:
        add_log(f"History unexpected error: {str(e)}", "CRITICAL")
        return {"success": False, "error": f"Unexpected Error: {str(e)}", "code": -1}

## Test for the module
if __name__ == '__main__':
    import time
    channel = 'chat'
    startStream(channel, callback=lambda ch, m: print(f"{ch}: {m}"))
    while True:
        status = send(channel, {"user": "tester", "message": "hello!!!"})
        print(f"Send status: {status}")
        time.sleep(1)
