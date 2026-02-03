import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API via the new Client architecture
API_KEY = os.getenv("GEMINI_API_KEY")

class TRCAIEngine:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=API_KEY) if API_KEY else None
        self.system_instruction = (
            "You are the Terminal Relay Controller (TRC) AI Orchestrator. "
            "You are embedded in a multi-channel terminal chat environment. "
            "Your goal is to assist technical teams by analyzing relay history, "
            "summarizing discussions, and proposing solutions to technical problems. "
            "When responding, keep it concise and formatted for a terminal (use ASCII highlights if needed). "
            "You have access to the history of multiple isolated channels via the TRC relay system."
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
                    system_instruction=self.system_instruction
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
                    system_instruction=self.system_instruction
                ),
                contents=f"{prompt}\n\n{context_text}"
            )
            return response.text
        except Exception as e:
            return f"❌ Pulse Generation Error: {str(e)}"

# Singleton instance
ai_engine = TRCAIEngine()
