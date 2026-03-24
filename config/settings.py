"""
Centralized application settings loaded from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application-wide configuration."""

    # --- Groq LLM ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "4096"))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.3"))

    # --- Data Fetch ---
    CACHE_TTL_REALTIME: int = 300        # 5 minutes
    CACHE_TTL_HISTORICAL: int = 3600     # 1 hour
    CACHE_TTL_NEWS: int = 900            # 15 minutes
    DEFAULT_LOOKBACK_DAYS: int = 365     # 1 year
    MAX_LOOKBACK_YEARS: int = 10

    # --- Analytics ---
    HERDING_WINDOW: int = 30             # Rolling window for herding detection
    PANIC_VOLUME_ZSCORE: float = 2.0     # Z-score threshold for volume spikes
    PANIC_DELIVERY_THRESHOLD: float = 30  # Below 30% delivery = speculative
    BEHAVIOR_GAP_SIP_AMOUNT: float = 10000  # Default SIP amount (INR)
    MONTE_CARLO_SIMULATIONS: int = 1000

    # --- App ---
    APP_NAME: str = "SheepOrSleep"
    APP_TAGLINE: str = "AI-Driven Behavioral Bias Detector for Indian Stocks"
    APP_VERSION: str = "1.0.0"

    @classmethod
    def validate(cls) -> list[str]:
        """Return list of configuration warnings."""
        warnings = []
        if not cls.GROQ_API_KEY:
            warnings.append("GROQ_API_KEY is not set. AI Copilot features will be unavailable.")
        return warnings


settings = Settings()
