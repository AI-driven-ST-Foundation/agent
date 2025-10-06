from typing import Optional
from src.AiHelper.config.config import Config
from src.AiHelper.utilities.imguploader._imgbb import ImgBBUploader
from src.AiHelper.utilities.imguploader._imghost import FreeImageHostUploader
from src.AiHelper.utilities.imguploader._magicuploader import MagicAPIUploader
from src.AiHelper.utilities.imguploader._imgbase import BaseImageUploader


class ImageUploader:
    def __init__(self, service: str = "auto"):
        self.config = Config()
        self.uploader: BaseImageUploader = self._select_uploader(service)

    def _select_uploader(self, service: str):
        if service == "imgbb" or (service == "auto" and self.config.IMGBB_API_KEY):
            return ImgBBUploader()
        elif service == "freeimagehost" or (service == "auto" and self.config.FREEIMAGEHOST_API_KEY):
            return FreeImageHostUploader()
        elif service == "magicapi" or (service == "auto" and self.config.FREEIMAGEHOST_API_KEY):
            return MagicAPIUploader()
        else:
            raise RuntimeError("Aucun service d'upload configuré. Vérifiez les clés API dans la config")

    def upload_from_file(self, file_path: str) -> Optional[str]:
        return self.uploader.upload_from_file(file_path)

    def upload_from_base64(self, base64_data: str) -> Optional[str]:
        return self.uploader.upload_from_base64(base64_data)


# still figuring out the best way to handle this but currently 
# to add : take an image path or base64 and return the url with fallback 
# if none of the providers works, return base64 

