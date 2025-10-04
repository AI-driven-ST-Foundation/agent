import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from typing import Optional, Dict, List, Union
import os
import base64
import requests
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
                    parts.append(content)
                elif isinstance(content, list):
                    # Complex content with text and/or images (OpenAI style)
                    parts = self._process_content_parts(content)
                else:
                    parts.append(str(content))
                
                # If there's a system message and this is the first user message, prepend it
                if system_message and not any(m.get("role") == "user" for m in gemini_messages):
                    parts.insert(0, system_message)
                    system_message = None  # Only add once
                
                gemini_messages.append({
                    "role": "user",
                    "parts": parts
                })
        
        return gemini_messages

    def _process_content_parts(self, content_list: List[Dict]) -> List:
        """
        Process content parts and convert images to Gemini format.
        
        Supports:
        - Text parts
        - OpenAI-style image_url format (URLs and base64 data URLs)
        - Native Gemini format
        
        Returns:
            List of parts suitable for Gemini API (strings and image data)
        """
        parts = []
        
        for item in content_list:
            if isinstance(item, str):
                parts.append(item)
                continue
                
            if not isinstance(item, dict):
                continue
            
            item_type = item.get("type")
            
            # Handle text content
            if item_type == "text":
                text = item.get("text", "")
                if text:
                    parts.append(text)
            
            # Handle OpenAI-style image_url format
            elif item_type == "image_url":
                image_data = self._process_image_url(item.get("image_url", {}))
                if image_data:
                    parts.append(image_data)
            
            # Handle native Gemini image format (if provided)
            elif item_type == "image":
                # Native Gemini format with inline_data
                if "inline_data" in item:
                    parts.append(item)
        
        return parts

    def _process_image_url(self, image_url_data: Dict) -> Optional[Dict]:
        """
        Process image URL and convert to Gemini format.
        
        Handles:
        - Regular URLs (fetches and converts to base64)
        - Base64 data URLs (extracts and converts)
        
        Returns:
            Dict with inline_data in Gemini format, or None if error
        """
        if not isinstance(image_url_data, dict):
            return None
        
        url = image_url_data.get("url", "")
        if not url:
            return None
        
        try:
            # Check if it's a base64 data URL
            if url.startswith("data:"):
                # Format: data:image/jpeg;base64,/9j/4AAQ...
                header, data = url.split(",", 1)
                media_type = header.split(";")[0].split(":")[1]
                
                # Gemini expects inline_data format
                return {
                    "inline_data": {
                        "mime_type": media_type,
                        "data": data
                    }
                }
            else:
                # Regular URL - fetch the image
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Determine MIME type from response headers
                mime_type = response.headers.get("content-type", "image/jpeg")
                
                # Convert to base64
                image_base64 = base64.b64encode(response.content).decode('utf-8')
                
                return {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_base64
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error processing image URL: {e}", True)
            return None

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
        
        # Check finish reason first
        finish_reason = response.candidates[0].finish_reason
        finish_reason_name = str(finish_reason)
        
        # Extract text from the first candidate
        try:
            content_text = response.text
        except Exception as e:
            # Handle safety filters and other issues
            self.logger.warning(f"Cannot extract text from response: {e}", True)
            
            # Check if it was blocked by safety filters
            if finish_reason == 2:  # SAFETY
                content_text = "[Content blocked by safety filters]"
                self.logger.warning("Response blocked by Gemini safety filters", True)
            elif finish_reason == 3:  # RECITATION
                content_text = "[Content blocked by recitation filter]"
                self.logger.warning("Response blocked by recitation filter", True)
            else:
                content_text = f"[No content available - finish_reason: {finish_reason_name}]"
        
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
            self.logger.info(f"Finish reason: {finish_reason_name}")
            result["finish_reason"] = finish_reason_name
            
        return result

