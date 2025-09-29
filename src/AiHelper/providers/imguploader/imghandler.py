from typing import Optional
from Libraries.AiHelper.config.config import Config
from Libraries.AiHelper.providers.imguploader._imgbb import ImgBBUploader
from Libraries.AiHelper.providers.imguploader._imghost import FreeImageHostUploader
from Libraries.AiHelper.providers.imguploader._magicuploader import MagicAPIUploader
from Libraries.AiHelper.providers.imguploader._imgbase import BaseImageUploader

class ImageUploader:
    
    def __init__(self, service: str = "auto"):
        self.config = Config()
        self.uploader: BaseImageUploader = self._select_uploader(service)

    def _select_uploader(self, service: str):
        #TODO: add fallback and logic of selecting provider based on catching exception
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

#quick test
if __name__ == "__main__":
    uploader = ImageUploader("magicapi")
    url = uploader.upload_from_base64("mkjqlkndfmk,nsdqmflk,sdfmlqsdkfnqdsmk,fdnqmkjd")
    print(url)