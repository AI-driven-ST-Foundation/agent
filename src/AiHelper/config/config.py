import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEFAULT_LLM_CLIENT = "openai"
    DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "")
    FREEIMAGEHOST_API_KEY = os.getenv("FREEIMAGEHOST_API_KEY", "")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

    # MAGICAPI_KEY = os.getenv("MAGICAPI_KEY", "")
    # DEFAULT_MAX_TOKENS = 1400
    # DEFAULT_TEMPERATURE = 1.0
    # DEFAULT_TOP_P = 1.0