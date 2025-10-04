import os
from dotenv import load_dotenv
from .model_config import ModelConfig

load_dotenv()


class Config:
    """
    Configuration class for AI Helper.
    Loads API keys from environment variables (.env file).
    Default models are loaded from llm_models.json (single source of truth).
    """
    
    # LLM Provider Settings
    DEFAULT_LLM_CLIENT = os.getenv("DEFAULT_LLM_CLIENT", "openai")
    
    # API Keys for LLM Providers
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Default Models per Provider
    _model_config = ModelConfig()
    DEFAULT_OPENAI_MODEL = os.getenv("DEFAULT_OPENAI_MODEL") or _model_config.get_provider_default_model("openai")
    DEFAULT_ANTHROPIC_MODEL = os.getenv("DEFAULT_ANTHROPIC_MODEL") or _model_config.get_provider_default_model("anthropic")
    DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL") or _model_config.get_provider_default_model("gemini")
    
    # Image Upload Provider API Keys
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
    FREEIMAGEHOST_API_KEY = os.getenv("FREEIMAGEHOST_API_KEY", "")

    # DEFAULT_MAX_TOKENS = 1400
    # DEFAULT_TEMPERATURE = 1.0
    # DEFAULT_TOP_P = 1.0