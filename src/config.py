import os
from dotenv import load_dotenv
from google import genai  # New SDK

# Load environment variables from .env file
load_dotenv()

# Get API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Initialize the client with the new SDK
genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# Model configuration
DEFAULT_MODEL = "gemini-2.0-flash"
AGENT_TEMPERATURE = 0.1
CHECKPOINT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "checkpoints")

# Ensure checkpoint directory exists
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
