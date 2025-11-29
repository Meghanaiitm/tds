# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
TIMEOUT_SECONDS = 30

# Add this line
QUIZ_SECRET = os.getenv("QUIZ_SECRET")