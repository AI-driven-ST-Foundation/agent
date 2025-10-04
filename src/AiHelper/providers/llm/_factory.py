from typing import Optional
from src.AiHelper.providers.llm._baseclient import BaseLLMClient
from src.AiHelper.providers.llm._openaiclient import OpenAIClient
from src.AiHelper.providers.llm._anthropic import AnthropicClient
from src.AiHelper.providers.llm._gemini import GeminiClient
from src.AiHelper.config.model_config import ModelConfig
from src.AiHelper.config.config import Config

class LLMClientFactory:
    """
    Factory class to create and return LLM client instances.
    Supports multiple providers: OpenAI, Anthropic (Claude), and Google Gemini.
    """
    
    # Load default models from configuration file
    _model_config = ModelConfig()
    DEFAULT_MODELS = {
        "openai": _model_config.get_provider_default_model("openai"),
        "anthropic": _model_config.get_provider_default_model("anthropic"),
        "gemini": _model_config.get_provider_default_model("gemini"),
    }
    
    @staticmethod
    def create_client(
        client_name: str = "openai", 
        model: Optional[str] = None
    ) -> BaseLLMClient:
        """
        Create and return an LLM client instance.
        
        Args:
            client_name: Name of the provider ('openai', 'anthropic', 'gemini')
            model: Model name to use (if None, uses default for the provider)
            
        Returns:
            BaseLLMClient instance
            
        Raises:
            ValueError: If the client_name is not supported
        """
        client_name_lower = client_name.lower()
        config = Config()
        
        # Use default model if not specified
        if model is None:
            model = LLMClientFactory.DEFAULT_MODELS.get(client_name_lower)
        
        if client_name_lower == "openai":
            api_key = config.OPENAI_API_KEY
            return OpenAIClient(model=model, api_key=api_key)
        elif client_name_lower == "anthropic" or client_name_lower == "claude":
            api_key = config.ANTHROPIC_API_KEY
            return AnthropicClient(model=model, api_key=api_key)
        elif client_name_lower == "gemini" or client_name_lower == "google":
            api_key = config.GEMINI_API_KEY
            return GeminiClient(model=model)
        
        # Future implementations
        elif client_name_lower == "deepseek":
            raise NotImplementedError("Deepseek is not implemented yet")
        elif client_name_lower == "huggingface":
            raise NotImplementedError("Huggingface is not implemented yet")
        elif client_name_lower == "litellm":
            raise NotImplementedError("Litellm is not implemented yet")
        else:
            supported = list(LLMClientFactory.DEFAULT_MODELS.keys())
            raise ValueError(
                f"Unsupported LLM client: {client_name}. "
                f"Supported providers: {', '.join(supported)}"
            )
