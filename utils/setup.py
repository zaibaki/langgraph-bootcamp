"""
utils/setup.py - Environment Setup and Validation
================================================

Common utilities for setting up and validating the development environment
across all sessions.
"""

import os
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variables and validate required API keys.
    
    Returns:
        bool: True if all required keys are available, False otherwise
    """
    load_dotenv()
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    print("🔑 Loading environment variables...")
    
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env file!")
        print("💡 Add your OpenAI API key to the .env file")
        return False
    
    if not TAVILY_API_KEY:
        print("❌ TAVILY_API_KEY not found in .env file!")
        print("💡 Add your Tavily API key to the .env file")
        return False
    
    print("✅ Environment loaded successfully")
    return True

def get_api_keys():
    """
    Get API keys for use in modules.
    
    Returns:
        tuple: (openai_key, tavily_key)
    """
    return os.getenv("OPENAI_API_KEY"), os.getenv("TAVILY_API_KEY")

def validate_session_requirements(session_name: str, required_keys: list = None):
    """
    Validate requirements for a specific session.
    
    Args:
        session_name: Name of the session for error messages
        required_keys: List of required environment variables
        
    Returns:
        bool: True if all requirements met
    """
    if required_keys is None:
        required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    
    print(f"🧪 Validating {session_name} requirements...")
    
    missing_keys = []
    for key in required_keys:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing required keys for {session_name}: {', '.join(missing_keys)}")
        return False
    
    print(f"✅ {session_name} requirements validated")
    return True