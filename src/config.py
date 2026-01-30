"""Central configuration for the Poker Coach application.

Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory (project root)
BASE_DIR = Path(__file__).parent.parent

# Data directory - can be overridden via DATA_DIR env var
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))

# Database configuration
DATABASE_FILE = DATA_DIR / "poker_coach.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_FILE}")

# Quiz bank file
QUIZ_BANK_FILE = DATA_DIR / "quiz_bank.json"

# GTO ranges file
GTO_RANGES_FILE = DATA_DIR / "gto_ranges.json"

# Anthropic API configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
