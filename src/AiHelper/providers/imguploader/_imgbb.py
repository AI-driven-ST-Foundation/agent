import os
import requests
from typing import Optional
from src.AiHelper.common._logger import RobotCustomLogger
from src.AiHelper.config.config import Config
from src.AiHelper.providers.imguploader._imgbase import BaseImageUploader

class ImgBBUploader(BaseImageUploader):
    def __init__(self):
        self.config = Config()
        self.base_url = "https://api.imgbb.com/1/upload"
        self.headers = {'Accept': 'application/json'}
        self.logger = RobotCustomLogger()

    @property
    def api_key(self):
        api_key = self.config.IMGBB_API_KEY
        self.logger.info(f"API key from config file : {api_key}")
        if not api_key:
            self.logger.error("IMGBB_API_KEY not found in configuration")
        return api_key
    
    def _make_request(self, payload: dict, files: bool = False) -> Optional[str]:
        try:
            if files:
                response = requests.post(self.base_url, files=payload)
            else:
                response = requests.post(self.base_url, data=payload, headers=self.headers)
            response.raise_for_status()
            json_data = response.json()
            return self._extract_url(json_data)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API Request Failed: {e}")
            return None
        except ValueError:
            self.logger.error("Invalid JSON response from API")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error during image upload: {str(e)}")
            return None
        
    def _extract_url(self, json_data: dict) -> Optional[str]:
        data = json_data.get('data', {})
        self.logger.info(f"Data: {data}")
        return data.get('display_url')

    def upload_from_base64(self, base64_data: str, filename: str = "screenshot.png", expiration: Optional[int] = None) -> Optional[str]:

        payload = {
            'key': self.api_key,
            'image': base64_data,
            'name': filename
        }
        if expiration is not None:
            payload['expiration'] = str(expiration)
        return self._make_request(payload)

    def upload_from_file(self, file_path: str, expiration: Optional[int] = None) -> Optional[str]:
        try:
            with open(file_path, 'rb') as file:
                payload = {
                    'key': (None, self.api_key),
                    'image': (os.path.basename(file_path), file)
                }
                if expiration is not None:
                    self.logger.info(f"Expiration: {expiration}")
                    payload['expiration'] = (None, str(expiration))
                return self._make_request(payload, files=True)
        except FileNotFoundError:
            full_path = os.path.abspath(file_path)
            self.logger.error(f"File not found: {full_path}")
            raise FileNotFoundError(f"File not found: {full_path}")
            

# if __name__ == "__main__":
#     imgbb = ImgBBUploader()
#     current_directory = os.getcwd()
#     url = imgbb.upload_from_file(f"{current_directory}/FeaturesLibrary/OpenAI/common/communauto.png")
#     if url:
#         print(f"File Uploaded image URL: {url}")
#     imgbase64 = "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"
#     url = imgbb.upload_from_base64(imgbase64)
#     if url:
#         print(f"Base64 Uploaded image URL: {url}")