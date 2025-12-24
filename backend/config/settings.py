import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    TAVILY_MAX_RESULTS: int = 4
    
    # Agent configuration
    CONFIDENCE_THRESHOLD: int = 7
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment")
        if not cls.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY not found in environment")

settings = Settings()
