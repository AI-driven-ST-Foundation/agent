import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from typing import Optional, Dict, List, Union
import os
from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.providers.llm._baseclient import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """
    Google Gemini API client implementing the BaseLLMClient interface.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        max_retries: int = 3,
    ):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key (if None, will try to load from config)
            model: Default model to use
            max_retries: Maximum number of retry attempts
        """
        self.logger = RobotCustomLogger()
        self.api_key: str = api_key
        
        if not self.api_key:
            from src.AiHelper.config.config import Config
            config = Config()
            self.api_key = config.GEMINI_API_KEY
            self.logger.info(f"API key loaded from config file")
            
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or in the environment variables.")
            
        self.default_model = model
        self.max_retries = max_retries
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Gemini SDK uses full model names with "models/" prefix in some cases
        # but GenerativeModel expects just the model name without prefix
        model_name = model.replace("models/", "") if model.startswith("models/") else model
        self.client = genai.GenerativeModel(model_name=model_name)

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1400,
        temperature: float = 1.0,
        top_p: float = 1.0,
        **kwargs
    ) -> Optional[GenerateContentResponse]:
        """
        Create a chat completion using Gemini API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (if None, uses default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            top_p: Nucleus sampling parameter (0-1)
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            Gemini GenerateContentResponse object
        """
        try:
            self._validate_parameters(temperature, top_p)
            
            # If a different model is requested, create a new model instance
            if model and model != self.default_model:
                client = genai.GenerativeModel(model_name=model)
            else:
                client = self.client
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            
            # Generate content
            response = client.generate_content(
                gemini_messages,
                generation_config=generation_config
            )
            
            # Log usage (Gemini provides token counts in usage_metadata)
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                total_tokens = (
                    response.usage_metadata.prompt_token_count + 
                    response.usage_metadata.candidates_token_count
                )
                self.logger.info(f"Gemini API call successful. Tokens used: {total_tokens}", True)
            else:
                self.logger.info(f"Gemini API call successful (no usage metadata available)", True)
            
            self.logger.info(f"Response: {response}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Gemini API Error: {str(e)}", True)
            raise

    def _convert_messages_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Convert standard message format to Gemini format.
        Gemini uses 'user' and 'model' roles instead of 'user' and 'assistant'.
        System messages are prepended to the first user message.
        Handles complex content structures (text + images).
        """
        gemini_messages = []
        system_message = None
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            
            if role == "system":
                system_message = content if isinstance(content, str) else str(content)
            elif role == "assistant":
                # Handle assistant messages
                if isinstance(content, str):
                    gemini_messages.append({
                        "role": "model",
                        "parts": [content]
                    })
                else:
                    gemini_messages.append({
                        "role": "model",
                        "parts": [str(content)]
                    })
            elif role == "user":
                # Handle user messages - can be string or complex content list
                parts = []
                
                if isinstance(content, str):
                    # Simple text message
                    text_content = content
                elif isinstance(content, list):
                    # Complex content with text and/or images (OpenAI style)
                    # Gemini only uses text, so extract text parts
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                text_parts.append(item.get("text", ""))
                            # Skip image_url parts as Gemini handles them differently
                            # In production, you'd need to fetch and convert images
                        elif isinstance(item, str):
                            text_parts.append(item)
                    text_content = "\n".join(text_parts)
                else:
                    text_content = str(content)
                
                # If there's a system message and this is the first user message, prepend it
                if system_message and not any(m.get("role") == "user" for m in gemini_messages):
                    text_content = f"{system_message}\n\n{text_content}"
                    system_message = None  # Only add once
                
                gemini_messages.append({
                    "role": "user",
                    "parts": [text_content]
                })
        
        return gemini_messages

    def _validate_parameters(self, temperature: float, top_p: float):
        """Validate API parameters."""
        if not (0 <= temperature <= 2):
            self.logger.error(f"Invalid temperature {temperature}. Must be between 0 and 2")
            raise ValueError(f"Invalid temperature {temperature}. Must be between 0 and 2")
        if not (0 <= top_p <= 1):
            self.logger.error(f"Invalid top_p {top_p}. Must be between 0 and 1")
            raise ValueError(f"Invalid top_p {top_p}. Must be between 0 and 1")

    def format_response(
        self, 
        response: GenerateContentResponse,
        include_tokens: bool = True,
        include_reason: bool = False
    ) -> Dict[str, Union[str, int]]:
        """
        Format Gemini response to a standardized dictionary.
        
        Args:
            response: Gemini GenerateContentResponse object
            include_tokens: Whether to include token usage information
            include_reason: Whether to include finish reason
            
        Returns:
            Standardized response dictionary
        """
        if not response or not response.candidates:
            self.logger.error(f"Invalid response or no candidates in the response", True)
            return {}
        
        # Extract text from the first candidate
        try:
            content_text = response.text
        except Exception as e:
            self.logger.error(f"Error extracting text from response: {e}", True)
            content_text = ""
        
        result = {
            "content": content_text,
        }
        
        if include_tokens and hasattr(response, 'usage_metadata') and response.usage_metadata:
            prompt_tokens = response.usage_metadata.prompt_token_count
            completion_tokens = response.usage_metadata.candidates_token_count
            total_tokens = prompt_tokens + completion_tokens
            
            self.logger.info(f"Tokens used: input={prompt_tokens}, output={completion_tokens}")
            result.update({
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            })
        
        if include_reason and response.candidates:
            finish_reason = response.candidates[0].finish_reason
            self.logger.info(f"Finish reason: {finish_reason}")
            result["finish_reason"] = str(finish_reason)
            
        return result

