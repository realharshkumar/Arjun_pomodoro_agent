import os
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
PORT = int(os.getenv("PORT", "8000"))
SARVAM_BASE_URL = "https://api.sarvam.ai"
