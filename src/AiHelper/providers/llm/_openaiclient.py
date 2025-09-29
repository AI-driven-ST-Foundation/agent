from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional, Dict, List, Union
import os
from dotenv import load_dotenv
from Libraries.AiHelper.common._logger import RobotCustomLogger
from Libraries.AiHelper.providers.llm._baseclient import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    
    def __init__(
        self, 
        api_key=None,
        model: str = "gpt-4o",
        max_retries: int = 3,
        base_backoff: int = 2,
    ):
        self.api_key : str = api_key
        if not self.api_key:
            from Libraries.AiHelper.config.config import Config
            config = Config()
            self.api_key = config.OPENAI_API_KEY
            self.logger.info(f"API key from config file : {self.api_key}")
            
        if not self.api_key:
            raise ValueError("API key must be provided either as an argument or in the environment variables.")
            
        self.default_model = model
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.client = OpenAI(api_key=self.api_key)
        self.logger = RobotCustomLogger()

    def create_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 1.0,
        top_p: float = 1.0,
        **kwargs
    ) -> Optional[ChatCompletion]:
        try:
            self._validate_parameters(temperature, top_p)
            
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            self.logger.info(f"OpenAI API call successful. Tokens used: {response.usage.total_tokens}",True)
            self.logger.info(f"messages: {response}")
            return response
        except Exception as e:
            self.logger.error(f"OpenAI API Error: {str(e)}",True)
            raise

    def _validate_parameters(self, temperature: float, top_p: float):
        if not (0 <= temperature <= 2):
            self.logger.error(f"Invalid temperature {temperature}. Must be between 0 and 2")
            raise ValueError(f"Invalid temperature {temperature}. Must be between 0 and 2")
        if not (0 <= top_p <= 1):
            self.logger.error(f"Invalid top_p {top_p}. Must be between 0 and 1")
            raise ValueError(f"Invalid top_p {top_p}. Must be between 0 and 1")

    def format_response(
        self, 
        response: ChatCompletion,
        include_tokens: bool = True,
        include_reason: bool = False
    ) -> Dict[str, Union[str, int]]:
        if not response or not response.choices:
            self.logger.error(f"Invalid response or no choices in the response", True, True)
            return {}
            
        result = {
            "content": response.choices[0].message.content,
        }
        
        if include_tokens:
            self.logger.info(f"Tokens used: {response.usage}")
            result.update({
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            })
            
        if include_reason:
            self.logger.info(f"Finish reason: {response.choices[0].finish_reason}")
            result["finish_reason"] = response.choices[0].finish_reason
            
        return result


# #quick test
# if __name__ == "__main__":
#     client = OpenAIClient()
#     messages1= [
#         {
#         "role": "user",
#         "content": [
#             {
#             "type": "text",
#             "text": "could you check if the destination goncourt is displayed on this screenshot ?"
#             },
#             {
#             "type": "image_url",
#             "image_url": {
#                 "url": "https://i.ibb.co/XZbVFrM7/screenshot-png.jpg"
#                 }
#             }
#         ]
#     }
#     ]
#     messages2 = [
#             {
#             'role': 'system', 
#             'content': "Vous êtes un expert en tests logiciels d'applications mobiles"
#             }, 

#             {
#             'role': 'user', 
#             'content': 
#             [
#                 {
#                 'type': 'text', 
#                 'text': 'est ce la destination goncourt a été affiché sur cet écran ?'
#                 },
#                 {
#                 'type': 'image_url', 
#                 'image_url': {
#                     'url': 'https://i.ibb.co/0RvxGMZr/screenshot-png.jpg'
#                     }
#                 }
#             ]
#         }
#     ]
#     response = client.create_chat_completion(messages2)
#     result = client.format_response(response)
#     print(result)