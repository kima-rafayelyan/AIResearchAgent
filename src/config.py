import os

from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "gemini-2.5-flash")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


MAX_SEARCH_ITERATIONS = 5
