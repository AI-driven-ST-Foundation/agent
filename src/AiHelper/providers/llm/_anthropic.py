from anthropic import Anthropic, APIError
from typing import Optional, Dict, List, Union
import os
from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.providers.llm._baseclient import BaseLLMClient


class AnthropicClient(BaseLLMClient):

    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_retries: int = 3,
    ):
        self.logger = RobotCustomLogger()
        self.api_key: str = api_key
        
        if not self.api_key:
            from src.AiHelper.config.config import Config
            config = Config()
            self.api_key = config.ANTHROPIC_API_KEY
            self.logger.info(f"API key loaded from config file")
            
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or in the environment variables.")
            
        self.default_model = model
        self.max_retries = max_retries
        self.client = Anthropic(api_key=self.api_key, max_retries=max_retries)

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1400,
        temperature: float = 1.0,
        top_p: float = 1.0,
        **kwargs
    ):
        """
        Create a chat completion using Anthropic API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (if None, uses default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter (0-1)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Anthropic Message object
        """
        try:
            self._validate_parameters(temperature, top_p)
            
            # Anthropic requires system messages to be separated
            system_message = None
            user_messages = []
            
            for msg in messages:
                if msg.get("role") == "system":
                    system_message = msg.get("content")
                else:
                    user_messages.append({
                        "role": msg.get("role"),
                        "content": msg.get("content")
                    })
            
            # Prepare API call parameters
            api_params = {
                "model": model or self.default_model,
                "messages": user_messages,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            # Only add temperature or top_p, not both (Anthropic requirement)
            if temperature != 1.0:
                api_params["temperature"] = temperature
            elif top_p != 1.0:
                api_params["top_p"] = top_p
            else:
                # If both are default, use temperature
                api_params["temperature"] = temperature
            
            if system_message:
                api_params["system"] = system_message
            
            response = self.client.messages.create(**api_params)
            
            # Log usage
            self.logger.info(
                f"Anthropic API call successful. Tokens used: {response.usage.input_tokens + response.usage.output_tokens}",
                True
            )
            self.logger.info(f"Response: {response}")
            
            return response
            
        except APIError as e:
            self.logger.error(f"Anthropic API Error: {str(e)}", True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}", True)
            raise

    def _validate_parameters(self, temperature: float, top_p: float):
        """Validate API parameters."""
        if not (0 <= temperature <= 1):
            self.logger.error(f"Invalid temperature {temperature}. Must be between 0 and 1 for Anthropic")
            raise ValueError(f"Invalid temperature {temperature}. Must be between 0 and 1")
        if not (0 <= top_p <= 1):
            self.logger.error(f"Invalid top_p {top_p}. Must be between 0 and 1")
            raise ValueError(f"Invalid top_p {top_p}. Must be between 0 and 1")

    def format_response(
        self, 
        response,
        include_tokens: bool = True,
        include_reason: bool = False
    ) -> Dict[str, Union[str, int]]:
        """
        Format Anthropic response to a standardized dictionary.
        
        Args:
            response: Anthropic Message object
            include_tokens: Whether to include token usage information
            include_reason: Whether to include stop reason
            
        Returns:
            Standardized response dictionary
        """
        if not response or not response.content:
            self.logger.error(f"Invalid response or no content in the response", True)
            return {}
        
        # Extract text content (Anthropic returns list of content blocks)
        content_text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content_text += block.text
        
        result = {
            "content": content_text,
        }
        
        if include_tokens and response.usage:
            self.logger.info(f"Tokens used: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
            result.update({
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            })
            
        if include_reason:
            self.logger.info(f"Stop reason: {response.stop_reason}")
            result["finish_reason"] = response.stop_reason
            
        return result

