import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import database
import communication

# Load environment variables
load_dotenv()

# Configure the Gemini API via the new Client architecture
API_KEY = os.getenv("GEMINI_API_KEY")

def read_channel_history(channel: str, limit: int = 50) -> str:
    """Reads the local technical history for a specific relay channel.
    
    Args:
        channel: The channel name (e.g., 'general', 'production-logs').
        limit: Number of recent messages to retrieve.
    """
    # Import locally to avoid color code issues if any, using standard ANSI
    MAGENTA = "\033[35m"
    RESET = "\033[0m"
    print(f"{MAGENTA}🛠️  [Tool] Gemini is reading history for #{channel}...{RESET}")
    
    history = database.get_local_history(channel, limit=limit)
    if not history:
        return f"No history found for channel #{channel}."
    
    formatted = f"HISTORY FOR #{channel}:\n"
    for m in history:
        formatted += f"[{m['timestamp']}] {m['user']}: {m['message']}\n"
    return formatted

def get_active_relays() -> str:
    """Returns a list of all active relay channels currently monitored by TRC."""
    MAGENTA = "\033[35m"
    RESET = "\033[0m"
    print(f"{MAGENTA}🛠️  [Tool] Gemini is checking active relay network...{RESET}")
    
    channels = communication.getActiveChannels()
    if not channels:
        return "No active relays currently monitored."
    return "Active Relays: #" + ", #".join(channels)

def read_local_file(path: str) -> str:
    """Reads the content of a local file in the TRC project directory.
    
    Args:
        path: Relative path to the file (e.g., 'ai_engine.py', 'chat.py').
    """
    MAGENTA = "\033[35m"
    RESET = "\033[0m"
    print(f"{MAGENTA}🛠️  [Tool] Gemini is reading file: {path}...{RESET}")
    
    try:
        # Basic security: prevent traversing up directories
        if ".." in path or path.startswith("/") or path.startswith("\\"):
             return "❌ Error: Access denied. Paths must be relative to the project root."
             
        if not os.path.exists(path):
            return f"❌ Error: File not found at {path}"
            
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"

def write_local_file(path: str, content: str) -> str:
    """Writes or overwrites content to a local file in the TRC project directory.
    
    Args:
        path: Relative path to the file.
        content: The text content to write.
    """
    MAGENTA = "\033[35m"
    RESET = "\033[0m"
    print(f"{MAGENTA}🛠️  [Tool] Gemini is modifying file: {path}...{RESET}")
    
    try:
        # Basic security: prevent traversing up directories
        if ".." in path or path.startswith("/") or path.startswith("\\"):
             return "❌ Error: Access denied. Paths must be relative to the project root."
             
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Successfully wrote to {path}"
    except Exception as e:
        return f"❌ Error writing file: {str(e)}"

class TRCAIEngine:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=API_KEY) if API_KEY else None
        # Define available tools (Gemini 2.5/3 currently don't support combining search with custom functions)
        self.tools = [
            read_channel_history, 
            get_active_relays,
            read_local_file,
            write_local_file
        ]
        self.system_instruction = (
            "You are the Terminal Relay Controller (TRC) AI Orchestrator. "
            "You are embedded in a multi-channel terminal chat environment. "
            "Your goal is to assist technical teams by analyzing relay history, "
            "summarizing discussions, and proposing/applying solutions to technical problems. "
            "When responding, keep it concise and formatted for a terminal (use ASCII highlights if needed). "
            "You have access to the history of multiple isolated channels via the TRC relay system, "
            "and you can read/write local project files to help debug or implement features discussed by the team. "
            "In 'Monitor Mode', you act as a silent guardian: only alert the team if you detect a high-severity "
            "technical risk, an unhandled error, or a major blocker."
        )

    def generate_response(self, prompt, channel="general", context_messages=None):
        """Generate a response using the Gemini model with optional context"""
        if not self.client:
            return "⚠️ Gemini API Key not found. Please set GEMINI_API_KEY in your .env file."

        try:
            # Fetch channel topic for context
            topic = database.get_channel_topic(channel)
            topic_context = f"CURRENT OBJECTIVE (# {channel}): {topic}\n" if topic else ""
            
            full_prompt = prompt
            if context_messages:
                # Format context for the model
                formatted_context = "\n".join([f"[{m['timestamp']}] {m['user']}: {m['message']}" for m in context_messages])
                full_prompt = f"{topic_context}Relay Context:\n{formatted_context}\n\nUser Query: {prompt}"
            else:
                full_prompt = f"{topic_context}User Query: {prompt}"

            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=self.tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                ),
                contents=full_prompt
            )
            return response.text
        except Exception as e:
            return f"❌ AI Engine Error: {str(e)}"

    def get_pulse(self, multi_channel_history):
        """Analyze multi-channel history and provide a high-level summary"""
        if not self.client:
            return "⚠️ Gemini API Key not found."

        try:
            prompt = (
                "Analyze the following multi-channel relay history and provide a 'Pulse Report'. "
                "Summarize active technical discussions, identify potential blockers or errors, "
                "and highlight team progress across all relayed channels."
            )
            
            # Format multi-channel history
            context_text = "MULTI-CHANNEL RELAY HISTORY:\n"
            for channel, messages in multi_channel_history.items():
                context_text += f"\n--- Channel: #{channel} ---\n"
                for m in messages:
                    context_text += f"[{m['timestamp']}] {m['user']}: {m['message']}\n"

            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=self.tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                ),
                contents=f"{prompt}\n\n{context_text}"
            )
            return response.text
        except Exception as e:
            return f"❌ Pulse Generation Error: {str(e)}"

    def analyze_image(self, image_path, user_prompt=None):
        """Analyze a local image file using multimodal capabilities"""
        if not self.client:
            return "⚠️ Gemini API Key not found."

        if not os.path.exists(image_path):
            return f"❌ Error: File not found at {image_path}"

        try:
            # Prepare prompt
            prompt = user_prompt if user_prompt else "Analyze this technical image/screenshot and provide a diagnosis."
            
            # Read image data
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Determine mime type based on extension
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"

            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=self.tools,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
                ),
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_data, mime_type=mime_type)
                ]
            )
            return response.text
        except Exception as e:
            return f"❌ Vision Engine Error: {str(e)}"

    def detect_anomalies(self, messages, channel="general"):
        """Passively analyze a batch of messages for technical risks or errors."""
        if not self.client or not messages:
            return None

        try:
            # Fetch channel topic for context
            topic = database.get_channel_topic(channel)
            topic_context = f"CURRENT OBJECTIVE: {topic}\n" if topic else ""

            # Format the messages for analysis
            formatted_messages = "\n".join([f"[{m['user']}]: {m['message']}" for m in messages])
            
            prompt = (
                f"{topic_context}\"Analyze the following recent messages from #{channel}.\n"
                "If you detect a high-severity technical anomaly, a recurring error, a security risk, "
                "or a critical blocker that prevents the team from reaching the objective, "
                "return a response starting with 'ALERT:'. Otherwise, return 'STATUS: OK'.\n\n"
                f"Messages:\n{formatted_messages}"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    # No tools for passive monitoring to prevent accidental file writes in background
                ),
                contents=prompt
            )
            
            text = response.text.strip()
            if text.upper().startswith("ALERT:"):
                return text
            return None # No anomaly detected
        except Exception:
            return None

# Singleton instance
ai_engine = TRCAIEngine()
