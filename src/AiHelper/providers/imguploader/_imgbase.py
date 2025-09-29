from abc import ABC, abstractmethod
from typing import Optional

class BaseImageUploader(ABC):
    """ Class de base pour les uploaders d'images"""
        
    @abstractmethod
    def upload_from_file(self, file_path: str) -> Optional[str]:
        """Upload an image from a file path.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Optional[str]: The URL of the uploaded image, or None if upload failed
        """
        pass
    
    @abstractmethod
    def upload_from_base64(self, base64_data: str) -> Optional[str]:
        """Upload an image from base64 data.
        
        Args:
            base64_data: The base64 encoded image data
            
        Returns:
            Optional[str]: The URL of the uploaded image, or None if upload failed
            
        Raises:
            NotImplementedError: If the uploader doesn't support base64 upload
        """
        pass