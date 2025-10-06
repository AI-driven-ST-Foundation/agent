import unittest
from unittest.mock import patch
from typing import List
from src.AiHelper.utilities.imguploader.imghandler import ImageUploader
from src.AiHelper.config.config import Config

class TestImageUploader(unittest.TestCase):
    
    def setUp(self):
        self.base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        self.warnings = []

    def _capture_warning(self, message: str):
        """Capture warning messages for verification"""
        self.warnings.append(message)

    def test_upload_with_imgbb(self):
        """Test upload with ImgBB configured and successful"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_imgbb_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None), \
             patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
            
            mock_upload.return_value = 'https://i.ibb.co/test123/image.png'
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertEqual(result, 'https://i.ibb.co/test123/image.png')

    def test_upload_with_freeimagehost(self):
        """Test upload with FreeImageHost configured and successful"""
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', 'fake_freeimagehost_key'), \
             patch('src.AiHelper.utilities.imguploader._imghost.FreeImageHostUploader.upload_from_base64') as mock_upload:
            
            mock_upload.return_value = 'https://freeimage.host/test456/image.png'
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertEqual(result, 'https://freeimage.host/test456/image.png')

    def test_upload_without_provider(self):
        """Test fallback when no provider is configured"""
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None):
            
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertIsNone(result)

    def test_upload_returning_none(self):
        """Test fallback when upload returns None"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None), \
             patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
            
            mock_upload.return_value = None
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertIsNone(result)

    def test_upload_with_exception(self):
        """Test fallback when an exception is raised"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None), \
             patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
            
            mock_upload.side_effect = Exception("Network error: Connection timeout")
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertIsNone(result)

    def test_auto_select_imgbb(self):
        """Test automatic selection of ImgBB"""
        with patch.object(Config, 'IMGBB_API_KEY', 'fake_imgbb_key'), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', 'fake_freeimagehost_key'), \
             patch('src.AiHelper.utilities.imguploader._imgbb.ImgBBUploader.upload_from_base64') as mock_upload:
            
            mock_upload.return_value = 'https://i.ibb.co/auto/image.png'
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertEqual(result, 'https://i.ibb.co/auto/image.png')

    def test_auto_select_freeimagehost(self):
        """Test automatic selection of FreeImageHost when ImgBB is not available"""
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', 'fake_freeimagehost_key'), \
             patch('src.AiHelper.utilities.imguploader._imghost.FreeImageHostUploader.upload_from_base64') as mock_upload:
            
            mock_upload.return_value = 'https://freeimage.host/auto/image.png'
            uploader = ImageUploader(service="auto")
            result = uploader.upload_from_base64(self.base64_data)
            
            self.assertEqual(result, 'https://freeimage.host/auto/image.png')

    def test_get_warning_messages(self):
        """Retrieve generated warning messages"""
        self.warnings = []
        with patch.object(Config, 'IMGBB_API_KEY', None), \
             patch.object(Config, 'FREEIMAGEHOST_API_KEY', None), \
             patch('src.AiHelper.utilities._logger.RobotCustomLogger.warning', side_effect=self._capture_warning):
            
            uploader = ImageUploader(service="auto")
            uploader.upload_from_base64(self.base64_data)
        
        self.assertGreater(len(self.warnings), 0)

if __name__ == '__main__':
    unittest.main()
