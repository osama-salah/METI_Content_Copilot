from google import genai
from google.genai import types
import json
from pathlib import Path

# Get the directory of the current script
script_dir = Path(__file__).parent
# Construct path to prompts.json
prompts_path = script_dir / "prompts" /"prompts.json"
prompts = json.load(open(prompts_path, "r"))
# Initialize the GenAI client with your API key
client = genai.Client(api_key="XXXXXXXXXXXXXXX")
copilot = client.chats.create(model="gemini-2.5-flash" , config=types.GenerateContentConfig(system_instruction=prompts["system"]["prompt"]),)
