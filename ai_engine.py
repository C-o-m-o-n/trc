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
    history = database.get_local_history(channel, limit=limit)
    if not history:
        return f"No history found for channel #{channel}."
    
    formatted = f"HISTORY FOR #{channel}:\n"
    for m in history:
        formatted += f"[{m['timestamp']}] {m['user']}: {m['message']}\n"
    return formatted

def get_active_relays() -> str:
    """Returns a list of all active relay channels currently monitored by TRC."""
    channels = communication.getActiveChannels()
    if not channels:
        return "No active relays currently monitored."
    return "Active Relays: #" + ", #".join(channels)

class TRCAIEngine:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=API_KEY) if API_KEY else None
        # Define available tools
        self.tools = [
            read_channel_history, 
            get_active_relays, 
            types.Tool(google_search=types.GoogleSearch())
        ]
        self.system_instruction = (
            "You are the Terminal Relay Controller (TRC) AI Orchestrator. "
            "You are embedded in a multi-channel terminal chat environment. "
            "Your goal is to assist technical teams by analyzing relay history, "
            "summarizing discussions, and proposing solutions to technical problems. "
            "When responding, keep it concise and formatted for a terminal (use ASCII highlights if needed). "
            "You have access to the history of multiple isolated channels via the TRC relay system and can search the web for technical documentation."
        )

    def generate_response(self, prompt, context_messages=None):
        """Generate a response using the Gemini model with optional context"""
        if not self.client:
            return "⚠️ Gemini API Key not found. Please set GEMINI_API_KEY in your .env file."

        try:
            full_prompt = prompt
            if context_messages:
                # Format context for the model
                formatted_context = "\n".join([f"[{m['timestamp']}] {m['user']}: {m['message']}" for m in context_messages])
                full_prompt = f"Relay Context:\n{formatted_context}\n\nUser Query: {prompt}"

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

# Singleton instance
ai_engine = TRCAIEngine()
