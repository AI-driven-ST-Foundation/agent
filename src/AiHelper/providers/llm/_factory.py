from typing import Optional
from src.AiHelper.providers.llm._baseclient import BaseLLMClient
from src.AiHelper.providers.llm._openaiclient import OpenAIClient

class LLMClientFactory:
    @staticmethod
    def create_client(client_name: str = "openai", api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> BaseLLMClient:
        """
        interface to create and return LLM client instances.
        """
        if client_name.lower() == "openai":
            return OpenAIClient(api_key, model=model)
        # TODO: add other implementations deepseek, gemini huggingface 
        elif client_name.lower() == "deepseek":
            raise NotImplementedError("Deepseek is not implemented yet")
        elif client_name.lower() == "gemini":
            raise NotImplementedError("Gemini is not implemented yet")
        elif client_name.lower() == "huggingface":
            raise NotImplementedError("Huggingface is not implemented yet")
        elif client_name.lower() == "litellm":
            raise NotImplementedError("Litellm is not implemented yet")
        else:
            raise ValueError(f"Unsupported LLM client: {client_name}")
