import os
import requests
from typing import Optional
from src.AiHelper.config.config import Config
from src.AiHelper.utilities._logger import RobotCustomLogger
from src.AiHelper.utilities.imguploader._imgbase import BaseImageUploader


class MagicAPIUploader(BaseImageUploader):
    def __init__(self):
        self.config = Config()
        self.logger = RobotCustomLogger()
        self.base_url = "https://api.magicapi.dev/api/v1/image-upload/upload"
        self.headers = {"accept": "application/json", "x-magicapi-key": self.api_key}

    @property
    def api_key(self):
        api_key = self.config.MAGICAPI_KEY
        if not api_key:
            self.logger.error("MAGICAPI_KEY not found in configuration")
        return api_key

    def _make_request(self, files: dict) -> Optional[str]:
        try:
            response = requests.post(self.base_url, headers=self.headers, files=files)
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
        return json_data.get("url")

    def upload_from_file(self, file_path: str) -> Optional[str]:
        self.logger.info(f"Uploading image from file: {file_path}")
        try:
            with open(file_path, "rb") as file:
                files = {"filename": (os.path.basename(file_path), file, "image/png")}
                return self._make_request(files)
        except FileNotFoundError:
            self.logger.error(f"File not found: {os.path.abspath(file_path)}")
            return None
        except IOError as e:
            self.logger.error(f"File access error: {str(e)}")
            return None


